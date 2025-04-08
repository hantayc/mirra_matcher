# responsibilities_match_score.py

import json
from match_alogorithm.utils.semantic_similarity import (
    nlp_similarity_cached,
)  # Ensure this module is in your PYTHONPATH


def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def extract_job_responsibilities_hard_skills(job_json):
    return job_json.get("responsibility", {}).get("hard_skills", [])


def extract_resume_skills(resume_json):
    return resume_json.get("skills", [])


def compute_required_skill_similarity(candidate_skill, job_required_skill):
    """
    Computes a similarity score between candidate skill(s) and a job-required skill.
    Normalizes candidate_skill and job_required_skill into groups and returns the maximum average similarity.
    """
    # Normalize candidate_skill into groups.
    if isinstance(candidate_skill, str):
        candidate_groups = [[candidate_skill]]
    elif isinstance(candidate_skill, list):
        if candidate_skill and isinstance(candidate_skill[0], list):
            candidate_groups = candidate_skill
        else:
            candidate_groups = [candidate_skill]
    else:
        candidate_groups = []

    # Normalize job_required_skill into groups.
    if isinstance(job_required_skill, list) and job_required_skill:
        if not isinstance(job_required_skill[0], list):
            job_required_groups = [job_required_skill]
        else:
            job_required_groups = job_required_skill
    else:
        job_required_groups = []

    if not candidate_groups or not job_required_groups:
        return None  # Missing requirements

    best_overall = 0.0
    for req_group in job_required_groups:
        # print(f"\nProcessing Job Requirement Group: {req_group}")
        best_for_req = 0.0
        for cand_group in candidate_groups:
            candidate_term_avgs = []
            # print(f"  Evaluating Candidate Group: {cand_group}")
            for cand_term in cand_group:
                sims = []
                for req_term in req_group:
                    sim = nlp_similarity_cached(cand_term, req_term)
                    # print(f"    '{cand_term}' vs. '{req_term}': similarity = {sim}")
                    sims.append(sim)
                if sims:
                    avg_sim = sum(sims) / len(sims)
                    # print(f"    => Average similarity for '{cand_term}': {avg_sim}")
                    candidate_term_avgs.append(avg_sim)
            if candidate_term_avgs:
                group_avg = max(candidate_term_avgs)
                # print(f"  => Best average for group {cand_group}: {group_avg}")
                if group_avg == 1.0:
                    return 1.0
                if group_avg > best_for_req:
                    best_for_req = group_avg
        if best_for_req > best_overall:
            best_overall = best_for_req
    # print(f"\n   --> Best overall similarity: {best_overall}")
    return best_overall


def calculate_responsibilities_match_score(job_json, resume_json):
    """
    Computes the overall responsibilities match score for a single job.
    If no responsibilities are specified in the job JSON, returns None.
    """
    job_responsibilities = extract_job_responsibilities_hard_skills(job_json)
    if not job_responsibilities:
        # print("=> No responsibilities specified in job description.")
        return None
    candidate_responsibilities = extract_resume_skills(resume_json)
    responsibility_scores = []
    for resp in job_responsibilities:
        required_resp = resp.get("skill", [])
        # print("\n--- Checking Job Responsibility ---")
        # print("Required Responsibility:")
        # print(json.dumps(required_resp, indent=4))
        best_sim = 0.0
        for candidate in candidate_responsibilities:
            candidate_resp = candidate.get("skill", [])
            sim = compute_required_skill_similarity(candidate_resp, required_resp)
            # print(f"Candidate Responsibility: {candidate_resp} -> Similarity: {sim}")
            if sim is not None and sim > best_sim:
                best_sim = sim
        # print(f"=> Best match for responsibility: {best_sim}\n")
        responsibility_scores.append(best_sim)
    overall_resp = safe_average(responsibility_scores)
    return overall_resp


def calculate_overall_responsibilities_match_score(job_json, resume_json):
    overall_resp = calculate_responsibilities_match_score(job_json, resume_json)
    # Return the result as a dictionary with key "responsibilities_score"
    return {"responsibilities_score": overall_resp}


def calculate_responsibilities_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects and returns a dictionary mapping each job's
    job_id to its responsibilities score dictionary.
    The returned dictionary has keys equal to the job's job_id and values equal to a dictionary
    with a single key "responsibilities_score".
    """
    results = {}
    for job_json in job_json_list:
        score_dict = calculate_overall_responsibilities_match_score(
            job_json, resume_json
        )
        job_id = job_json.get("job_id")
        results[job_id] = score_dict
    return results


if __name__ == "__main__":
    # Example usage:
    # Replace these with your actual list of job JSON objects (each with a "job_id" key)
    # and a resume JSON object.
    job_json_list = []  # List of job JSON objects
    resume_json = {}  # Your resume JSON object
    results = calculate_responsibilities_scores(job_json_list, resume_json)
    print("Responsibilities Scores for Jobs:")
    print(results)
