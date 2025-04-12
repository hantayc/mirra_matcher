import math
import numpy as np
from match_alogorithm.utils.semantic_similarity import nlp_similarity_cached

def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None

def extract_job_mandatory_skills(job_json):
    return job_json.get("mandatory", {}).get("hard_skills", [])

def extract_resume_skills(resume_json):
    return resume_json.get("skills", [])

def compute_group_similarity(candidate_group, required_group):
    """
    For a multi-term required_group (e.g. ["Salesforce dev", "Apex"]),
    find the best match for each required term among candidate_group,
    then average those best matches.
    """
    if not candidate_group or not required_group:
        return 0.0

    sims_for_required_terms = []
    for req_term in required_group:
        best_for_req_term = 0.0
        for cand_term in candidate_group:
            sim = nlp_similarity_cached(cand_term, req_term)
            if sim > best_for_req_term:
                best_for_req_term = sim
        sims_for_required_terms.append(best_for_req_term)
    return sum(sims_for_required_terms) / len(sims_for_required_terms)

def compute_required_skill_similarity(candidate_skill_item, job_required_skill):
    """
    Each job_required_skill can be a list of multiple sub-groups
    e.g. [ ["Salesforce dev", "Apex"], ["Salesforce.com development", "Apex"] ].
    We compute the group similarity for each subgroup and pick the maximum.
    """
    if not job_required_skill:
        return 0.0

    if isinstance(job_required_skill[0], str):
        # wrap a single group
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
    For each job_id in the resume, pick the single best similarity and the max years.
    Returns a list of dicts of the form:
        { "job_id": ..., "sim": <best similarity>, "years": <max years> }
    Only job_ids with sim > 0 are kept.
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
    We:
      1. Aggregate best entries per job_id.
      2. Sort them (using NumPy) in descending order by similarity.
      3. Iterate through the sorted entries, summing their contributions (weighted by the fraction
         of the required years) until min_years_required is met.
      4. Implement an early exit: if we encounter an entry with sim >= 0.9 and its available years
         are sufficient to meet the remaining needed years, we treat it as a perfect match and stop.
    """

    if not resume_skills or not job_required_skill:
        return 0.0

    best_entries = aggregate_best_entries(resume_skills, job_required_skill)
    if not best_entries:
        return 0.0

    # Sort the entries by similarity descending using NumPy.
    sim_values = np.array([entry["sim"] for entry in best_entries])
    sorted_indices = np.argsort(-sim_values)
    best_entries = [best_entries[i] for i in sorted_indices]

    coverage_used = 0.0
    weighted_sum = 0.0
    coverage_mode = None  # either "empty" or "real"
    needed = float(min_years_required)

    for item in best_entries:
        jbid = item["job_id"]
        sim = item["sim"]
        yrs = item["years"]

        if sim >= 0.9 and yrs >= needed:
            weighted_sum = 1.0  # We treat sim >= 0.9 as perfect (1.0)
            coverage_used = min_years_required
            break

        if coverage_used >= min_years_required:
            break

        if coverage_mode is None:
            if jbid.strip() == "":
                # Empty job_id skill
                if yrs >= min_years_required:
                    fraction = 1.0
                    weighted_sum += sim * fraction
                    coverage_used += min_years_required
                    coverage_mode = "empty"
                    break
                else:
                    continue
            else:
                # Real job_id: start accumulating coverage.
                coverage_mode = "real"
                use_years = min(yrs, needed)
                fraction = use_years / float(min_years_required)
                weighted_sum += sim * fraction
                coverage_used += use_years
                needed -= use_years
        else:
            if coverage_mode == "empty":
                break
            else:
                if jbid.strip() == "":
                    continue
                else:
                    use_years = min(yrs, needed)
                    fraction = use_years / float(min_years_required)
                    weighted_sum += sim * fraction
                    coverage_used += use_years
                    needed -= use_years

    if coverage_used <= 0:
        return 0.0

    if coverage_used < min_years_required:
        return weighted_sum

    return weighted_sum

def calculate_skill_match_score(job_json, resume_json):
    """
    Iterates over each mandatory skill requirement in the job JSON,
    calls compute_single_requirement_score, and returns the average of all requirements.
    """

    job_skills = extract_job_mandatory_skills(job_json)
    if not job_skills:
        return None

    resume_skills = extract_resume_skills(resume_json)
    requirement_scores = []
    for idx, req in enumerate(job_skills, start=1):
        job_required_skill = req.get("skill", [])
        min_years_required = req.get("minyears", [0])[0]
        score_for_this_req = compute_single_requirement_score(resume_skills, job_required_skill, min_years_required)
        requirement_scores.append(score_for_this_req)

    overall_skill = safe_average(requirement_scores)
    if overall_skill is None:
        return None
    else:
        return overall_skill

def calculate_mandatory_skill_score(job_json, resume_json):
    return {"mandatory_skill_score": calculate_skill_match_score(job_json, resume_json)}

def calculate_mandatory_skill_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects and returns a dictionary mapping each job's
    job_id to its mandatory skill score.
    """
    results = {}
    for i, job_json in enumerate(job_json_list, start=1):
        job_id = job_json.get("job_id", f"job_{i}")
        score_dict = calculate_mandatory_skill_score(job_json, resume_json)
        results[job_id] = score_dict
    return results