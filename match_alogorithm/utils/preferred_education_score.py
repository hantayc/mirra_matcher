# preferred_education_score.py

import json
from match_alogorithm.utils.semantic_similarity import (
    nlp_similarity_cached,
)  # Ensure this module is accessible


def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


EDU_RANK = {
    "High School Diploma": 1,
    "Vocational": 1,
    "Associate's": 2,
    "Current Bachelor's Student": 3,
    "Some Bachelor's": 3,
    "Bachelor’s": 4,
    "Bachelor's": 4,
    "Some Master's": 5,
    "Current Master's Student": 5,
    "Master’s": 6,
    "Master's": 6,
    "PhD": 7,
    "Postdoctoral": 8,
}


def extract_job_education_requirements(job_json):
    return job_json.get("preferred", {}).get("education", [])


def extract_resume_education(resume_json):
    return resume_json.get("education", [])


def extract_professional_background(resume_json):
    return resume_json.get("professional_background", [])


def candidate_has_education_level(resume_education, required_rank):
    for edu in resume_education:
        level = edu.get("education_level", "")
        if EDU_RANK.get(level, 0) >= required_rank:
            return True
    return False


def get_required_field_score(
    resume_education,
    resume_experience,
    required_fields,
    must_have_formal,
    required_rank,
    threshold=0.6,
    min_years=4,
    ignore_threshold=False,
):
    similarity_scores = []
    for edu in resume_education:
        level = edu.get("education_level", "")
        if EDU_RANK.get(level, 0) >= required_rank:
            for candidate_major in edu.get("major", []):
                for req_field in required_fields:
                    sim_score = nlp_similarity_cached(candidate_major, req_field)
                    if not ignore_threshold:
                        effective_threshold = (
                            0.95 if req_field.lower() != "related" else threshold
                        )
                        if sim_score >= effective_threshold:
                            similarity_scores.append(sim_score)
                    else:
                        similarity_scores.append(sim_score)
    if similarity_scores:
        avg_score = sum(similarity_scores) / len(similarity_scores)
        return avg_score
    else:
        return get_equivalent_experience_score(
            resume_experience, required_fields, threshold=threshold, min_years=min_years
        )


def get_equivalent_experience_score(
    resume_experience, field_of_study_list, threshold=0.6, min_years=4
):
    total_years = 0.0
    weighted_sum = 0.0
    for exp in resume_experience:
        candidate_fields = exp.get("field_of_study", [])
        job_titles = exp.get("background", [])
        years = exp.get("years", 0)
        max_sim = 0.0
        for candidate_field in candidate_fields:
            for req_field in field_of_study_list:
                if req_field.lower() == "related":
                    continue
                sim_score = nlp_similarity_cached(candidate_field, req_field)
                if sim_score > max_sim:
                    max_sim = sim_score
        if max_sim >= threshold:
            weighted_sum += max_sim * years
            total_years += years
    if total_years >= min_years and total_years > 0:
        avg_exp = weighted_sum / total_years
        return avg_exp
    else:
        return 0.0


def meets_education_requirement(
    requirement,
    resume_education,
    resume_experience,
    threshold=0.7,
    min_years=4,
    allow_fallback=False,
):
    req_fields = requirement.get("field_of_study", [])
    req_levels = requirement.get("education_level", [])
    must_have_formal = True
    for lvl in req_levels:
        if "or experience" in lvl.lower():
            must_have_formal = False
            break
    if allow_fallback:
        must_have_formal = False
    max_required_rank = 0
    for lvl in req_levels:
        lvl_rank = EDU_RANK.get(lvl, 0)
        if lvl_rank > max_required_rank:
            max_required_rank = lvl_rank
    level_scores = []
    if req_fields:
        if must_have_formal:
            formal_score = get_required_field_score(
                resume_education,
                resume_experience,
                req_fields,
                must_have_formal,
                max_required_rank,
                threshold,
                min_years,
                ignore_threshold=False,
            )
            level_scores.append(formal_score)
        else:
            formal_score = get_required_field_score(
                resume_education,
                resume_experience,
                req_fields,
                must_have_formal,
                max_required_rank,
                threshold,
                min_years,
                ignore_threshold=True,
            )
            exp_score = get_equivalent_experience_score(
                resume_experience, req_fields, threshold, min_years
            )
            combined_score = (
                (formal_score + exp_score) / 2
                if (formal_score > 0 and exp_score > 0)
                else (formal_score or exp_score)
            )
            level_scores.append(combined_score)
    else:
        if must_have_formal:
            level_scores.append(
                1.0
                if candidate_has_education_level(resume_education, max_required_rank)
                else 0.0
            )
        else:
            level_scores.append(
                1.0
                if candidate_has_education_level(resume_education, max_required_rank)
                else get_equivalent_experience_score(
                    resume_experience, ["Any"], threshold, min_years
                )
            )
    overall_req_score = safe_average(level_scores) if level_scores else 0.0
    return overall_req_score


def calculate_preferred_education_score(
    job_json, resume_json, threshold=0.7, min_years=4
):
    pref_requirements = extract_job_education_requirements(job_json)
    resume_edu = extract_resume_education(resume_json)
    resume_exp = extract_professional_background(resume_json)
    if not pref_requirements:
        return {"preferred_education_score": None}
    preferred_scores = []
    for req in pref_requirements:
        score = meets_education_requirement(
            req, resume_edu, resume_exp, threshold, min_years, allow_fallback=True
        )
        preferred_scores.append(score)
    pref_avg = safe_average(preferred_scores)
    return {"preferred_education_score": pref_avg}


def calculate_preferred_education_scores(job_json_list, resume_json):
    results = {}
    for job_json in job_json_list:
        score = calculate_preferred_education_score(job_json, resume_json)
        job_id = job_json.get("job_id")
        results[job_id] = score
    return results


if __name__ == "__main__":
    job_json_list = []  # Fill with your job JSON objects
    resume_json = {}  # Your resume JSON object
    results = calculate_preferred_education_scores(job_json_list, resume_json)
    # print("Preferred Education Scores for Jobs:")
    # print(json.dumps(results, indent=4))
