# preferred_background_score.py

import json
from utils.semantic_similarity import (
    nlp_similarity_cached,
)  # Ensure this module is accessible


def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


# ---------------------------
# Extraction Function
# ---------------------------
def extract_professional_background(resume_json):
    return resume_json.get("professional_background", [])


# ---------------------------
# Background Matching
# ---------------------------
def get_background_match_score(
    job_req_background,
    candidate_prof_background,
    job_details,
    threshold=0.6,
    min_years_required=4,
):
    """
    Computes a weighted average similarity score for candidate background (role) matches.
    Special Case: If any job requirement group contains "Work Experience" or "Working Experience",
    then we sum the candidate's total background years.
    Returns weighted_avg = sum(max_similarity * years) / sum(years), or 0.0 if total years < min_years_required.
    """
    # print("\n== Starting Background Match Score Calculation ==")
    # print("Job Requirement Background Groups:")
    for idx, group in enumerate(job_req_background, start=1):
        pass  # print(f"  Group {idx}: {group}")

    work_experience_mode = any(
        any(term.lower() in ["work experience", "working experience"] for term in group)
        for group in job_req_background
    )

    if work_experience_mode:
        # print("=> 'Work Experience' detected. Using special mode (years only).")
        total_candidate_years = sum(
            entry.get("years", 0) for entry in candidate_prof_background
        )
        # print(f"   Total Candidate Background Years: {total_candidate_years}")
        if total_candidate_years >= min_years_required:
            # print(f"=> Candidate meets the work experience requirement (Required: {min_years_required} years). Returning 1.0.\n")
            return 1.0
        else:
            # print(f"=> Candidate does NOT meet the work experience requirement (Required: {min_years_required} years). Returning 0.0.\n")
            return 0.0

    total_years = 0.0
    weighted_sum = 0.0

    for entry in candidate_prof_background:
        years = entry.get("years", 0)
        candidate_terms = entry.get("background", [])
        # print("\n--- Processing Candidate Background Entry ---")
        # print(f"Candidate Background Terms: {candidate_terms}")
        entry_max = 0.0
        for candidate_term in candidate_terms:
            group_scores = []
            # print(f"\nEvaluating Candidate Term: '{candidate_term}'")
            for group in job_req_background:
                if len(group) > 1:
                    sims = [
                        nlp_similarity_cached(candidate_term, term) for term in group
                    ]
                    group_score = sum(sims) / len(sims)
                    # print(f"  Against Group {group}: similarities = {sims}, average = {group_score}")
                else:
                    group_score = nlp_similarity_cached(candidate_term, group[0])
                    # print(f"  Against Group {group}: similarity = {group_score}")
                group_scores.append(group_score)
            if group_scores:
                candidate_term_score = max(group_scores)
                # print(f"=> Max similarity for candidate term '{candidate_term}': {candidate_term_score}")
                if candidate_term_score > entry_max:
                    entry_max = candidate_term_score
        # print(f"Maximum similarity for candidate entry: {entry_max}")
        if entry_max >= threshold:
            weighted_sum += entry_max * years
            total_years += years
            # print(f"=> Adding {years} years weighted by {entry_max} (Contribution: {entry_max * years}).")
        #    print(f"=> Cumulative Relevant Background Years: {total_years}\n")

    if total_years >= min_years_required and total_years > 0:
        avg_bg_score = weighted_sum / total_years
        # print(f"=> Total Background Experience: {total_years} years (Required: {min_years_required} years)")
        # print(f"=> Weighted Average Background Score: {avg_bg_score}\n")
        return avg_bg_score
    else:
        # print(f"=> Total Background Experience: {total_years} years (Required: {min_years_required} years) -- Not enough experience. Returning 0.0.\n")
        return 0.0


# ---------------------------
# Industry Matching
# ---------------------------
def get_industry_match_score(
    req_industries, candidate_prof_background, threshold=0.6, min_years_required=4
):
    """
    Computes a weighted average similarity score for candidate industry matches.
    Returns weighted_avg = sum(max_similarity * years) / sum(years), or 0.0 if total years < min_years_required.
    """
    # print("\n== Starting Industry Match Score Calculation ==")
    # print(f"Job Requirement Industries: {req_industries}")
    total_years = 0.0
    weighted_sum = 0.0
    for entry in candidate_prof_background:
        years = entry.get("years", 0)
        candidate_industries = entry.get("industry", [])
        # print("\n--- Processing Candidate Industry Entry ---")
        # print(f"Candidate Industries: {candidate_industries}")
        entry_max = 0.0
        for cand_ind in candidate_industries:
            for req_ind in req_industries:
                sim = nlp_similarity_cached(cand_ind, req_ind)
                # print(f"  '{cand_ind}' vs. '{req_ind}': similarity = {sim}")
                if sim > entry_max:
                    entry_max = sim
        # print(f"=> Maximum industry similarity for this entry: {entry_max}")
        if entry_max >= threshold:
            weighted_sum += entry_max * years
            total_years += years
            # print(f"=> Adding {years} years weighted by {entry_max} (Contribution: {entry_max * years}).")
    if total_years >= min_years_required and total_years > 0:
        avg_ind_score = weighted_sum / total_years
        # print(f"=> Total Industry Experience: {total_years} years (Required: {min_years_required} years)")
        # print(f"=> Weighted Average Industry Score: {avg_ind_score}\n")
        return avg_ind_score
    else:
        # print(f"=> Total Industry Experience: {total_years} years (Required: {min_years_required} years) -- Not enough experience. Returning 0.0.\n")
        return 0.0


# ---------------------------
# Preferred Background Scoring for a Single Job
# ---------------------------
def calculate_preferred_background_score(job_json, resume_json, threshold=0.6):
    job_req = job_json.get("preferred", {}).get("professional_background", [])
    candidate_background = extract_professional_background(resume_json)
    job_details = job_json.get("details", {})

    if not job_req:
        # print("=> No preferred professional background requirements specified.\n")
        return None, None

    bg_scores = []
    ind_scores = []
    for req in job_req:
        req_minyears = req.get("minyears", [0])[0]
        req_background = req.get("background", [])
        req_industries = req.get("industry", [])
        # print(f"\n--- Processing Preferred Background Requirement (Min Years: {req_minyears}) ---")
        bg_score = get_background_match_score(
            req_background, candidate_background, job_details, threshold, req_minyears
        )
        # print(f"=> Background Score for requirement: {bg_score}")
        if req_industries:
            ind_score = get_industry_match_score(
                req_industries, candidate_background, threshold, req_minyears
            )
            # print(f"=> Industry Score for requirement: {ind_score}\n")
        else:
            ind_score = None
            # print("=> No industry requirements specified for this requirement.\n")
        bg_scores.append(bg_score)
        ind_scores.append(ind_score)
    pref_bg_avg = safe_average(bg_scores)
    pref_ind_avg = (
        safe_average(ind_scores)
        if ind_scores and any(ind is not None for ind in ind_scores)
        else None
    )
    return pref_bg_avg, pref_ind_avg


def calculate_preferred_background_scores(job_json_list, resume_json, threshold=0.6):
    """
    Accepts a list of job JSON objects and returns a dictionary mapping each job's
    job_id to its preferred background scores.
    The returned dictionary uses the job's "job_id" as the key and a dictionary with keys:
         "preferred_background_score" and "preferred_industry_score"
    as the value.
    """
    results = {}
    for job_json in job_json_list:
        pref_bg, pref_ind = calculate_preferred_background_score(
            job_json, resume_json, threshold
        )
        job_id = job_json.get("job_id")
        results[job_id] = {
            "preferred_background_score": pref_bg,
            "preferred_industry_score": pref_ind,
        }
    return results


if __name__ == "__main__":
    # Example usage:
    # Replace these with your actual list of job JSON objects (each with "job_id")
    # and your resume JSON object.
    job_json_list = []  # List of job JSON objects
    resume_json = {}  # Your resume JSON object
    results = calculate_preferred_background_scores(
        job_json_list, resume_json, threshold=0.6
    )
    # The returned dictionary will have keys equal to each job's "job_id" and values like:
    # { "preferred_background_score": score, "preferred_industry_score": score }
    print("Preferred Background Scores for Jobs:")
    print(results)
