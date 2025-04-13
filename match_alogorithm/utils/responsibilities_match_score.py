# responsibilities_match_score.py
import numpy as np
from match_alogorithm.utils.semantic_similarity import get_embedding
import faiss

###############################################
# Helper functions
###############################################
def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None

def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("normalize_text expects a string, but got a non-string value.")
    return text.strip()

###############################################
# FAISS Helper Functions
###############################################
def build_faiss_index_for_terms(terms):
    """
    Given a list of text terms, compute their embeddings using get_embedding,
    normalize them, and build a FAISS index (using inner product, which is cosine
    similarity if vectors are normalized).
    Returns the FAISS index.
    """
    embeddings = []
    for term in terms:
        emb = get_embedding(term).detach().cpu().numpy().astype(np.float32)
        norm_val = np.linalg.norm(emb)
        if norm_val > 0:
            emb = emb / norm_val
        embeddings.append(emb)
    embeddings = np.vstack(embeddings)
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    return index

def faiss_group_similarity(candidate_texts, required_texts):
    """
    Given a list of candidate_texts and required_texts (both lists of strings),
    builds a FAISS index from candidate_texts and for each required text retrieves
    the best cosine similarity. Returns the average best similarity.
    """
    if not candidate_texts or not required_texts:
        return 0.0

    index = build_faiss_index_for_terms(candidate_texts)
    sims = []
    for req_text in required_texts:
        req_emb = get_embedding(req_text).detach().cpu().numpy().astype(np.float32)
        norm_val = np.linalg.norm(req_emb)
        if norm_val > 0:
            req_emb = req_emb / norm_val
        req_emb = np.expand_dims(req_emb, axis=0)
        distances, indices = index.search(req_emb, 1)
        best_sim = distances[0][0]
        sims.append(best_sim)
    return sum(sims) / len(sims)

###############################################
# Normalization of Responsibility Inputs
###############################################
def normalize_candidate_responsibility(candidate_resp):
    """
    Accepts candidate responsibility input. If it's a string, wraps it as [[string]].
    If it's a list of strings, returns [list-of-strings].
    If it's already a list of lists, returns it unchanged.
    """
    if isinstance(candidate_resp, str):
        return [[candidate_resp]]
    elif isinstance(candidate_resp, list):
        if candidate_resp and isinstance(candidate_resp[0], list):
            return candidate_resp
        else:
            return [candidate_resp]
    else:
        return []

def normalize_required_responsibility(required_resp):
    """
    Similar to normalize_candidate_responsibility but for job required responsibility input.
    """
    if isinstance(required_resp, str):
        return [[required_resp]]
    elif isinstance(required_resp, list):
        if required_resp and isinstance(required_resp[0], list):
            return required_resp
        else:
            return [required_resp]
    else:
        return []

###############################################
# Responsibilities Similarity Functions (Using FAISS)
###############################################
def compute_responsibility_similarity(candidate_resp, job_required_resp):
    """
    Computes a similarity score between candidate responsibility and required responsibility.
    Each input (candidate_resp and job_required_resp) is normalized into groups.
    For each required group, we compute the average best similarity (via FAISS) with candidate groups.
    Returns the maximum similarity score over all required groups.
    """
    candidate_groups = normalize_candidate_responsibility(candidate_resp)
    required_groups = normalize_required_responsibility(job_required_resp)
    
    if not candidate_groups or not required_groups:
        return None

    best_overall = 0.0
    for req_group in required_groups:
        best_for_req = 0.0
        for cand_group in candidate_groups:
            sim_score = faiss_group_similarity(cand_group, req_group)
            if sim_score > best_for_req:
                best_for_req = sim_score
        if best_for_req > best_overall:
            best_overall = best_for_req
    return best_overall

###############################################
# Extraction Functions (No mention of "skills")
###############################################
def extract_job_responsibilities(job_json):
    """
    Assumes the job responsibilities are stored under:
        job_json["responsibility"]["responsibilities"]
    and that each responsibility is an object with a key "text" holding its description.
    """
    return job_json.get("responsibility", {}).get("responsibilities", [])

def extract_candidate_responsibilities(resume_json):
    """
    Assumes candidate (resume) responsibilities are stored under:
        resume_json["responsibilities"]
    and that each responsibility is an object with a key "text" holding its description.
    """
    return resume_json.get("responsibilities", [])

###############################################
# Overall Responsibilities Match Score
###############################################
def calculate_responsibilities_match_score(job_json, resume_json):
    """
    Computes the overall responsibilities match score for a single job.
    For each job responsibility, this function finds the best matching candidate responsibility
    (using FAISS-based similarity). Then, it averages these best-match similarities.
    """
    job_resps = extract_job_responsibilities(job_json)
    if not job_resps:
        return None
    candidate_resps = extract_candidate_responsibilities(resume_json)
    resp_scores = []
    for resp in job_resps:
        required_text = resp.get("text", "")  # each job responsibility is expected to have "text"
        best_sim = 0.0
        for candidate in candidate_resps:
            candidate_text = candidate.get("text", "")
            sim = compute_responsibility_similarity(candidate_text, required_text)
            if sim is not None and sim > best_sim:
                best_sim = sim
        resp_scores.append(best_sim)
    overall_resp = safe_average(resp_scores)
    return overall_resp

def calculate_overall_responsibilities_match_score(job_json, resume_json):
    overall_resp = calculate_responsibilities_match_score(job_json, resume_json)
    return {"responsibilities_score": overall_resp}

def calculate_responsibilities_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects and returns a dictionary mapping each job's
    job_id to its responsibilities match score.
    """
    results = {}
    for job_json in job_json_list:
        score_dict = calculate_overall_responsibilities_match_score(job_json, resume_json)
        job_id = job_json.get("job_id")
        results[job_id] = score_dict
    return results