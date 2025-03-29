from utils.semantic_similarity import nlp_similarity_cached
from utils.semantic_similarity import sentence_model
from utils.mandatory_skill_score import calculate_mandatory_skill_scores
from utils.preferred_skill_score import calculate_preferred_skill_scores
from utils.responsibilities_match_score import calculate_responsibilities_scores
from utils.mandatory_education_score import calculate_mandatory_education_scores
from utils.preferred_education_score import calculate_preferred_education_scores
from utils.mandatory_credentials_score import calculate_mandatory_credentials_scores
from utils.preferred_credentials_score import calculate_preferred_credentials_scores
from utils.mandatory_background_score import calculate_mandatory_background_scores
from utils.preferred_background_score import calculate_preferred_background_scores
from utils.merge_scores import merge_scores_by_job_id
from utils.overall_scores import make_overall_scores
import pandas as pd
import numpy as np
import json
import os


def calculate_match_score(job_desc_json_lst, canidate_resume_JSON):

    print(f"Total Length of Sample: {len(job_desc_json_lst)}")

    # Run Match Score
    # Stage 1:
    # 1.1. Calculate credentials scores
    mandatory_credentials_scores = calculate_mandatory_credentials_scores(
        job_json_list=job_desc_json_lst, resume_json=canidate_resume_JSON
    )
    preferred_credentials_scores = calculate_preferred_credentials_scores(
        job_json_list=job_desc_json_lst, resume_json=canidate_resume_JSON
    )

    # 1.2. Calculate education scores
    mandatory_education_scores = calculate_mandatory_education_scores(
        job_json_list=job_desc_json_lst, resume_json=canidate_resume_JSON
    )
    preferred_education_scores = calculate_preferred_education_scores(
        job_json_list=job_desc_json_lst, resume_json=canidate_resume_JSON
    )

    # 1.3. Calculate background scores
    mandatory_background_scores = calculate_mandatory_background_scores(
        job_json_list=job_desc_json_lst, resume_json=canidate_resume_JSON
    )
    preferred_background_scores = calculate_preferred_background_scores(
        job_json_list=job_desc_json_lst, resume_json=canidate_resume_JSON
    )

    # Stage 1.5: Filter after the first stage
    stage1_scores = merge_scores_by_job_id(
        mandatory_background_scores,
        preferred_background_scores,
        mandatory_education_scores,
        preferred_education_scores,
        mandatory_credentials_scores,
        preferred_credentials_scores,
        filter=True,
        threshold=0.5,
    )

    stage_job_desc_json_lst = [
        job
        for job in job_desc_json_lst
        if job.get("job_id") in set(stage1_scores.keys())
    ]

    print(f"Total Length of Sample after Stage 1: {len(stage_job_desc_json_lst)}")

    # Stage 2:
    # 2.1. Calculate responsibilities scores
    mandatory_responsibilities_scores = calculate_responsibilities_scores(
        job_json_list=stage_job_desc_json_lst, resume_json=canidate_resume_JSON
    )

    # 2.2. Calculate skills scores
    mandatory_skills_scores = calculate_mandatory_skill_scores(
        job_json_list=stage_job_desc_json_lst, resume_json=canidate_resume_JSON
    )
    preferred_skills_scores = calculate_preferred_skill_scores(
        job_json_list=stage_job_desc_json_lst, resume_json=canidate_resume_JSON
    )

    # Stage 2.5: Filter after the second stage
    stage2_scores = merge_scores_by_job_id(
        stage1_scores,  # append stage 1
        mandatory_responsibilities_scores,
        mandatory_skills_scores,
        preferred_skills_scores,
        filter=True,
        threshold=0.5,
    )

    print(f"Total Length of Sample after Stage 2: {len(stage2_scores)}")

    # Stage 3:
    results = make_overall_scores(stage2_scores)

    return results
