# preferred_skill_score.py

import json
from utils.semantic_similarity import (
    nlp_similarity_cached,
)  # Ensure this module is available


def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def extract_job_preferred_skills(job_json):
    return job_json.get("preferred", {}).get("hard_skills", [])


def extract_resume_skills(resume_json):
    return resume_json.get("skills", [])


def compute_required_skill_similarity(candidate_skill, job_required_skill):
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


def calculate_skill_match_score(job_json, resume_json):
    job_skills = extract_job_preferred_skills(job_json)
    if not job_skills:
        # print("=> No preferred skill requirements specified.")
        return None
    resume_skills = extract_resume_skills(resume_json)
    requirement_scores = []
    for req in job_skills:
        job_required_skill = req.get("skill", [])
        min_years_required = req.get("minyears", [0])[0]
        # print("----------------------------------------------------")
        # print("Processing Preferred Job Skill Requirement:")
        # print(f"  Requirement: {job_required_skill}")
        # print(f"  Minimum Years Required: {min_years_required}")
        best_match = 0.0
        for candidate in resume_skills:
            candidate_years = candidate.get("years", 0)
            if candidate_years >= min_years_required:
                for candidate_skill in candidate.get("skill", []):
                    sim = compute_required_skill_similarity(
                        candidate_skill, job_required_skill
                    )
                    if sim is not None and sim > best_match:
                        best_match = sim
        # print(f"  Best match for requirement: {best_match}")
        requirement_scores.append(best_match)
    overall_skill = safe_average(requirement_scores)
    # print(f"Overall Preferred Skill Match Score: {overall_skill}")
    return overall_skill


def calculate_preferred_skill_score(job_json, resume_json):
    pref_score = calculate_skill_match_score(job_json, resume_json)
    # Return only the preferred score without repeating the job_id inside the value.
    return {"preferred_skill_score": pref_score}


def calculate_preferred_skill_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects and returns a dictionary mapping each job's
    job_id to its preferred skill score.
    """
    results = {}
    for job_json in job_json_list:
        score_dict = calculate_preferred_skill_score(job_json, resume_json)
        job_id = job_json.get("job_id")
        results[job_id] = score_dict
    return results


if __name__ == "__main__":
    # Example usage:
    # Replace these with your actual list of job JSON objects and a resume JSON object.
    job_json_list = []  # List of job JSON objects with "job_id" defined
    resume_json = {}  # Your resume JSON object
    results = calculate_preferred_skill_scores(job_json_list, resume_json)
    # print("Preferred Skill Scores for Jobs:")
    print(results)
