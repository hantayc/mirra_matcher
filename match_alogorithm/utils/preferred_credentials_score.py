#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
credentials_score.py

A module that computes both mandatory and preferred credentials match scores,
using nested-list "OR" logic:
  - If the job credential is [ ["CISSP"], ["CISM"] ], we treat "CISSP OR CISM".
  - The resume does NOT have nested credential lists; each is a list of strings.

Functions:
  - calculate_mandatory_credentials_score(job_json, resume_json)
  - calculate_preferred_credentials_score(job_json, resume_json)
  - calculate_overall_credentials_score(job_json, resume_json)  # optional aggregator
  - calculate_mandatory_credentials_scores(job_json_list, resume_json)
  - calculate_preferred_credentials_scores(job_json_list, resume_json)

Example usage at bottom.

"""

import json
from match_alogorithm.utils.semantic_similarity import (
    nlp_similarity_cached,
)  # Adjust import path as needed


def safe_average(values):
    """Averaging function that ignores None."""
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def extract_job_mandatory_credentials(job_json):
    """
    Extracts mandatory credentials (list of objects) from the job JSON.
    For example:
      job_json["mandatory"]["credentials"] => [
        { "credential": [ ["CISSP"], ["CISM"] ] },
        { "credential": [ ["CRISC"] ] }
      ]
    """
    return job_json.get("mandatory", {}).get("credentials", [])


def extract_job_preferred_credentials(job_json):
    """
    Extracts preferred credentials (list of objects) from the job JSON.
    For example:
      job_json["preferred"]["credentials"] => [
        { "credential": [ ["CEH"] ] }
      ]
    """
    return job_json.get("preferred", {}).get("credentials", [])


def extract_resume_credentials(resume_json):
    """
    Extracts the candidate's credentials (list of objects).
    e.g. resume_json["credentials"] => [
      { "credential": ["AWS Certified Solutions Architect"] },
      { "credential": ["CISM"] }
    ]
    """
    return resume_json.get("credentials", [])


def compute_required_credential_similarity(
    candidate_credential, job_required_credential
):
    """
    Like your skill function:
      - candidate_credential = list of strings (NOT nested), e.g. ["CISM"]
      - job_required_credential can be nested (OR logic), e.g. [ ["CISSP"], ["CISM"] ]

    We find the maximum similarity in [0..1].
    """
    # Normalize candidate_credential => candidate_groups
    if isinstance(candidate_credential, str):
        candidate_groups = [[candidate_credential]]
    elif isinstance(candidate_credential, list):
        if candidate_credential and isinstance(candidate_credential[0], list):
            candidate_groups = candidate_credential
        else:
            candidate_groups = [candidate_credential]
    else:
        candidate_groups = []

    # Normalize job_required_credential => job_required_groups
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
    # For each sub-list in the job credential
    for req_group in job_required_groups:
        best_for_req = 0.0
        for cand_group in candidate_groups:
            candidate_term_sims = []
            for cand_term in cand_group:
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
    Goes through each required credential object in the job side, e.g.
      { "credential": [ ["CISSP"], ["CISM"] ] }
    Finds the best match across the candidate's credentials.
    Then averages those best matches across all required items.
    Returns a float [0..1] or None if no required creds exist.
    """
    if not required_creds:
        return None

    req_scores = []
    for req_cred_obj in required_creds:
        job_cred_list = req_cred_obj.get("credential", [])
        best_sim_for_req = 0.0

        # Compare to each candidate credential object
        for cand_obj in resume_creds:
            candidate_cred_list = cand_obj.get("credential", [])
            if isinstance(candidate_cred_list, str):
                candidate_cred_list = [candidate_cred_list]

            sim = compute_required_credential_similarity(
                candidate_cred_list, job_cred_list
            )
            if sim > best_sim_for_req:
                best_sim_for_req = sim

        req_scores.append(best_sim_for_req)

    if req_scores:
        overall_cred = sum(req_scores) / len(req_scores)
        return overall_cred
    else:
        return None


def calculate_mandatory_credentials_score(job_json, resume_json):
    """
    Returns average [0..1] for mandatory credentials, or None if no mandatory creds exist.
    """
    job_mandatory = extract_job_mandatory_credentials(job_json)
    resume_creds = extract_resume_credentials(resume_json)
    if not job_mandatory:
        return None
    return match_credentials(job_mandatory, resume_creds)


def calculate_preferred_credentials_score(job_json, resume_json):
    """
    Returns average [0..1] for preferred credentials, or None if no preferred creds exist.
    """
    job_preferred = extract_job_preferred_credentials(job_json)
    resume_creds = extract_resume_credentials(resume_json)
    if not job_preferred:
        return None
    return match_credentials(job_preferred, resume_creds)


def calculate_overall_credentials_score(
    job_json, resume_json, mandatory_weight=0.5, preferred_weight=0.5
):
    """
    Combines the mandatory and preferred credentials scores into a single weighted average.
    If one is None, we handle that gracefully.

    Returns a float [0..1], or None if both are None.
    """
    m_score = calculate_mandatory_credentials_score(job_json, resume_json)
    p_score = calculate_preferred_credentials_score(job_json, resume_json)

    if m_score is None and p_score is None:
        return None
    elif m_score is not None and p_score is not None:
        total_weight = mandatory_weight + preferred_weight
        return (m_score * mandatory_weight + p_score * preferred_weight) / total_weight
    elif m_score is not None:
        return m_score
    else:
        return p_score


def calculate_mandatory_credentials_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects and returns a dictionary mapping each job's
    job_id to its mandatory credentials score, e.g.:
      {
        "job-1": {"mandatory_credentials_score": 0.75},
        "job-2": {"mandatory_credentials_score": None}
      }
    """
    results = {}
    for job_json in job_json_list:
        job_id = job_json.get("job_id")
        score = calculate_mandatory_credentials_score(job_json, resume_json)
        results[job_id] = {"mandatory_credentials_score": score}
    return results


def calculate_preferred_credentials_scores(job_json_list, resume_json):
    """
    Similar to above, but for preferred credentials.
    """
    results = {}
    for job_json in job_json_list:
        job_id = job_json.get("job_id")
        score = calculate_preferred_credentials_score(job_json, resume_json)
        results[job_id] = {"preferred_credentials_score": score}
    return results
