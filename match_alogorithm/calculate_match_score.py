from concurrent.futures import ProcessPoolExecutor
from utils.semantic_similarity import nlp_similarity_cached, sentence_model
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


def calculate_match_score(job_desc_json_lst, candidate_resume_JSON):
    print(f"Total Length of Sample: {len(job_desc_json_lst)}")

    # -------------------------
    # Stage 1: Run 6 scoring functions in parallel
    # -------------------------
    with ProcessPoolExecutor() as executor:
        futures_stage1 = {
            "mandatory_credentials": executor.submit(
                calculate_mandatory_credentials_scores,
                job_desc_json_lst,
                candidate_resume_JSON,
            ),
            "preferred_credentials": executor.submit(
                calculate_preferred_credentials_scores,
                job_desc_json_lst,
                candidate_resume_JSON,
            ),
            "mandatory_education": executor.submit(
                calculate_mandatory_education_scores,
                job_desc_json_lst,
                candidate_resume_JSON,
            ),
            "preferred_education": executor.submit(
                calculate_preferred_education_scores,
                job_desc_json_lst,
                candidate_resume_JSON,
            ),
            "mandatory_background": executor.submit(
                calculate_mandatory_background_scores,
                job_desc_json_lst,
                candidate_resume_JSON,
            ),
            "preferred_background": executor.submit(
                calculate_preferred_background_scores,
                job_desc_json_lst,
                candidate_resume_JSON,
            ),
        }

        # Wait for all Stage 1 futures to complete
        mandatory_credentials_scores = futures_stage1["mandatory_credentials"].result()
        preferred_credentials_scores = futures_stage1["preferred_credentials"].result()
        mandatory_education_scores = futures_stage1["mandatory_education"].result()
        preferred_education_scores = futures_stage1["preferred_education"].result()
        mandatory_background_scores = futures_stage1["mandatory_background"].result()
        preferred_background_scores = futures_stage1["preferred_background"].result()

    # -------------------------
    # Stage 1.5: Filter after the first stage
    # -------------------------
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

    # -------------------------
    # Stage 2: Run 3 scoring functions in parallel
    # -------------------------
    with ProcessPoolExecutor() as executor:
        futures_stage2 = {
            "responsibilities": executor.submit(
                calculate_responsibilities_scores,
                job_json_list=stage_job_desc_json_lst,
                resume_json=candidate_resume_JSON,
            ),
            "mandatory_skills": executor.submit(
                calculate_mandatory_skill_scores,
                job_json_list=stage_job_desc_json_lst,
                resume_json=candidate_resume_JSON,
            ),
            "preferred_skills": executor.submit(
                calculate_preferred_skill_scores,
                job_json_list=stage_job_desc_json_lst,
                resume_json=candidate_resume_JSON,
            ),
        }

        # Wait for all Stage 2 futures to complete
        responsibilities_score = futures_stage2["responsibilities"].result()
        mandatory_skills_scores = futures_stage2["mandatory_skills"].result()
        preferred_skills_scores = futures_stage2["preferred_skills"].result()

    # -------------------------
    # Stage 2.5: Filter after the second stage
    # -------------------------
    stage2_scores = merge_scores_by_job_id(
        stage1_scores,
        responsibilities_score,
        mandatory_skills_scores,
        preferred_skills_scores,
        filter=True,
        threshold=0.5,
    )

    print(f"Total Length of Sample after Stage 2: {len(stage2_scores)}")

    # -------------------------
    # Stage 3: Compute overall scores
    # -------------------------
    results = make_overall_scores(stage2_scores)

    return results
