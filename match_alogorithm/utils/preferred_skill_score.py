import numpy as np
from match_alogorithm.utils.semantic_similarity import get_embedding
import faiss

########################################################################
# HELPERS & UTILITY FUNCTIONS
########################################################################
def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("normalize_text expects a string, but got a non-string value.")
    return text.strip()
    
########################################################################
# JOB & RESUME SKILL EXTRACTION
########################################################################
def extract_job_preferred_skills(job_json):
    return job_json.get("preferred", {}).get("hard_skills", [])

def extract_resume_skills(resume_json):
    return resume_json.get("skills", [])

########################################################################
# FAISS-BASED GROUP SIMILARITY
########################################################################
def build_faiss_index(terms):
    """
    Given a list of text terms, compute their embeddings and build a FAISS index
    using inner-product search (which works as cosine similarity if vectors are normalized).
    Returns the FAISS index and an array of embeddings.
    """
    embeddings = []
    for term in terms:
        emb = get_embedding(term).detach().cpu().numpy().astype(np.float32)
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm
        embeddings.append(emb)
    embeddings = np.vstack(embeddings)
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    return index, embeddings

def compute_group_similarity(candidate_group, required_group):
    """
    For a multi-term required_group (e.g. ["Salesforce dev", "Apex"]),
    build a FAISS index from candidate_group embeddings and for each required term,
    retrieve the highest similarity. Then, average these best similarities.
    """
    if not candidate_group or not required_group:
        return 0.0

    # Build FAISS index for candidate_group texts.
    index, _ = build_faiss_index(candidate_group)
    sims = []
    for req_term in required_group:
        req_emb = get_embedding(req_term).detach().cpu().numpy().astype(np.float32)
        norm = np.linalg.norm(req_emb)
        if norm > 0:
            req_emb = req_emb / norm
        req_emb = np.expand_dims(req_emb, axis=0)
        distances, indices = index.search(req_emb, 1)
        best_sim = distances[0][0]  # Inner product similarity
        sims.append(best_sim)
    return sum(sims) / len(sims)

########################################################################
# REQUIRED SKILL SIMILARITY & AGGREGATION
########################################################################
def compute_required_skill_similarity(candidate_skill_item, job_required_skill):
    """
    For a given candidate skill item and a job-required skill (which can be a list of sub-groups),
    compute the similarity as follows:
      - If job_required_skill is a single group, wrap it in a list.
      - For each subgroup in job_required_skill, compute the group similarity using FAISS.
      - Return the maximum similarity across subgroups.
    """
    if not job_required_skill:
        return 0.0

    if isinstance(job_required_skill[0], str):
        job_required_skill = [job_required_skill]

    candidate_group = candidate_skill_item.get("skill", [])
    if not candidate_group:
        return 0.0

    best_sim = 0.0
    for req_group in job_required_skill:
        sim_score = compute_group_similarity(candidate_group, req_group)
        if sim_score > best_sim:
            best_sim = sim_score
    return best_sim

def aggregate_best_entries(resume_skills, job_required_skill):
    """
    For each candidate skill item in resume_skills, compute its best similarity score 
    (using compute_required_skill_similarity) and record its maximum years.
    Then group by job_id and pick the highest similarity per job.
    Returns a list of dicts of the form:
      { "job_id": <job_id>, "sim": <best similarity>, "years": <max years> }
    Only entries with sim > 0 are kept.
    """
    by_job_id = {}
    for cand_skill_item in resume_skills:
        jbid = cand_skill_item.get("job_id", "")
        cand_years = cand_skill_item.get("years", 0.0)
        sim = compute_required_skill_similarity(cand_skill_item, job_required_skill)
        if jbid not in by_job_id:
            by_job_id[jbid] = {"sim": sim, "years": cand_years}
        else:
            if sim > by_job_id[jbid]["sim"]:
                by_job_id[jbid]["sim"] = sim
            if cand_years > by_job_id[jbid]["years"]:
                by_job_id[jbid]["years"] = cand_years
    result = []
    for jbid, vals in by_job_id.items():
        if vals["sim"] > 0.0:
            result.append({"job_id": jbid, "sim": vals["sim"], "years": vals["years"]})
    return result

def compute_single_requirement_score(resume_skills, job_required_skill, min_years_required):
    """
    Compute a weighted similarity score for a single requirement.
    1. Aggregate best entries (by job_id).
    2. Sort them in descending order by similarity.
    3. Iterate through the sorted entries, summing their contributions (weighted by the fraction
       of the required years) until min_years_required is met.
    If an entry with sim >= 0.9 can cover the remaining years, it is treated as a perfect match.
    """
    if not resume_skills or not job_required_skill:
        return 0.0

    best_entries = aggregate_best_entries(resume_skills, job_required_skill)
    if not best_entries:
        return 0.0

    # Sort entries by similarity descending.
    best_entries = sorted(best_entries, key=lambda x: x["sim"], reverse=True)
    coverage_used = 0.0
    weighted_sum = 0.0
    needed = float(min_years_required)

    for item in best_entries:
        jbid = item["job_id"]
        sim = item["sim"]
        yrs = item["years"]

        if sim >= 0.9 and yrs >= needed:
            weighted_sum = 1.0  # Perfect match for remaining requirement.
            coverage_used = min_years_required
            break

        if coverage_used >= min_years_required:
            break

        if jbid.strip() == "":
            continue

        use_years = min(yrs, needed)
        fraction = use_years / float(min_years_required)
        weighted_sum += sim * fraction
        coverage_used += use_years
        needed -= use_years

    if coverage_used < min_years_required:
        return weighted_sum
    return weighted_sum

########################################################################
# OVERALL MATCH SCORE CALCULATION
########################################################################
def calculate_skill_match_score(job_json, resume_json):
    """
    Iterates over each mandatory skill requirement in the job JSON,
    computes a weighted similarity score for each requirement,
    and returns the average of these scores.
    """
    job_skills = extract_job_preferred_skills(job_json)
    if not job_skills:
        return None

    resume_skills = extract_resume_skills(resume_json)
    requirement_scores = []
    for req in job_skills:
        job_required_skill = req.get("skill", [])
        min_years_required = req.get("minyears", [0])[0]
        score_for_this_req = compute_single_requirement_score(resume_skills, job_required_skill, min_years_required)
        requirement_scores.append(score_for_this_req)
    overall_skill = safe_average(requirement_scores)
    return overall_skill

def calculate_preferred_skill_score(job_json, resume_json):
    score = calculate_skill_match_score(job_json, resume_json)
    return {"preferred_skill_score": score}

def calculate_preferred_skill_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects and returns a dictionary mapping each job's
    job_id to its mandatory skill score.
    """
    results = {}
    for i, job_json in enumerate(job_json_list, start=1):
        job_id = job_json.get("job_id", f"job_{i}")
        score_dict = calculate_preferred_skill_score(job_json, resume_json)
        results[job_id] = score_dict
    return results