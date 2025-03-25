# mandatory_credentials_score.py

import json
from utils.semantic_similarity import nlp_similarity_cached


def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def extract_job_mandatory_credentials(job_json):
    """Extracts the mandatory credentials from the job description."""
    return job_json.get("mandatory", {}).get("credentials", [])


def extract_resume_credentials(resume_json):
    """Extracts the candidate's credentials from the resume."""
    return resume_json.get("credentials", [])


def compute_required_credential_similarity(
    candidate_credential, job_required_credential
):
    """
    Similar to your skill-matching logic. This function compares a single candidate credential
    (which can be a string or list of strings) to a job-required credential (potentially nested).

    - If 'job_required_credential' is like [ ["CISSP"], ["CISM"] ],
      that means "CISSP OR CISM."
    - If the first element isn't a list, we wrap it as one group.

    We return the maximum similarity found in [0..1].
    """

    # 1) Normalize candidate_credential into groups
    #    (But the resume won't have nested lists, so this is simpler.)
    if isinstance(candidate_credential, str):
        candidate_groups = [[candidate_credential]]
    elif isinstance(candidate_credential, list):
        # e.g. ["AWS Certified Solutions Architect"] => one group
        if candidate_credential and isinstance(candidate_credential[0], list):
            # If it were nested (unlikely for resumes), we'd keep it
            candidate_groups = candidate_credential
        else:
            candidate_groups = [candidate_credential]
    else:
        candidate_groups = []

    # 2) Normalize job_required_credential into groups
    #    e.g. if job_required_credential is [ ["CISSP"], ["CISM"] ],
    #    we call that multiple sub-lists => "OR" condition
    if isinstance(job_required_credential, list) and job_required_credential:
        if not isinstance(job_required_credential[0], list):
            job_required_groups = [job_required_credential]
        else:
            job_required_groups = job_required_credential
    else:
        job_required_groups = []

    if not candidate_groups or not job_required_groups:
        return 0.0

    best_overall = 0.0

    # For each sub-list in the job requirement (OR group)
    for req_group in job_required_groups:
        # e.g. req_group might be ["CISSP"]
        best_for_req = 0.0
        # Compare each candidate group
        for cand_group in candidate_groups:
            # e.g. cand_group might be ["AWS Certified Solutions Architect"]
            candidate_term_sims = []
            for cand_term in cand_group:
                # Compare to each term in req_group
                sims = []
                for req_term in req_group:
                    sim = nlp_similarity_cached(cand_term, req_term)
                    sims.append(sim)
                if sims:
                    avg_sim = sum(sims) / len(sims)
                    candidate_term_sims.append(avg_sim)
            if candidate_term_sims:
                group_best = max(candidate_term_sims)
                if group_best > best_for_req:
                    best_for_req = group_best
        if best_for_req > best_overall:
            best_overall = best_for_req

    return best_overall


def match_credentials(required_creds, resume_creds):
    """
    For each job credential object in 'required_creds', we retrieve 'credential'
    (potentially nested) and compare it to all candidate credentials. We store the
    best match. Then we average across all required items.

    If e.g. required_creds = [
        {"credential": [ ["CISSP"], ["CISM"] ]}
      ]
    we consider "CISSP OR CISM" for that item. If the candidate has multiple credentials,
    we pick the single best match for that item. Then we average across items.
    """

    if not required_creds:
        return None

    req_scores = []
    # Each item might look like: {"credential": [ ["CISSP"], ["CISM"] ]}
    for req_cred_obj in required_creds:
        job_cred_list = req_cred_obj.get("credential", [])
        best_sim_for_this_req = 0.0

        # We compare to each candidate credential object
        # e.g. resume_creds = [{"credential": ["AWS Certified Solutions Architect"]}, ...]
        for cand_obj in resume_creds:
            candidate_cred_list = cand_obj.get("credential", [])
            # candidate_cred_list is typically a list of strings (NOT nested)
            if isinstance(candidate_cred_list, str):
                # if the resume had a single string (less likely?), unify it
                candidate_cred_list = [candidate_cred_list]

            # Now compute the best possible match
            sim = compute_required_credential_similarity(
                candidate_cred_list, job_cred_list
            )
            if sim > best_sim_for_this_req:
                best_sim_for_this_req = sim

        req_scores.append(best_sim_for_this_req)

    if req_scores:
        return sum(req_scores) / len(req_scores)
    else:
        return None


def calculate_mandatory_credentials_score(job_json, resume_json):
    """
    If no mandatory credentials => returns None.
    Otherwise, returns an average similarity [0..1].
    """
    job_mandatory = extract_job_mandatory_credentials(job_json)
    resume_creds = extract_resume_credentials(resume_json)
    if not job_mandatory:
        return None
    score = match_credentials(job_mandatory, resume_creds)
    return score


def calculate_mandatory_credentials_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects (each must have "job_id") and returns a dict:
      {
        job_id: {"mandatory_credentials_score": float or None},
        ...
      }
    """
    results = {}
    for job_json in job_json_list:
        score = calculate_mandatory_credentials_score(job_json, resume_json)
        job_id = job_json.get("job_id")
        results[job_id] = {"mandatory_credentials_score": score}
    return results


if __name__ == "__main__":
    # Demo usage:
    example_job = {
        "job_id": "job-456",
        "mandatory": {"credentials": [{"credential": [["CISSP"], ["CISM"]]}]},
    }
    example_resume = {
        "credentials": [
            {"credential": ["CISM"]},
            {"credential": ["AWS Certified Solutions Architect"]},
        ]
    }
    single_score = calculate_mandatory_credentials_score(example_job, example_resume)
    print("Mandatory Credentials Score (single example):", single_score)

    job_list = [example_job]
    batch_scores = calculate_mandatory_credentials_scores(job_list, example_resume)
    print("\nBatch Scores:\n", batch_scores)
