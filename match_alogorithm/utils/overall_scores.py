def make_overall_scores(
    job_scores_dict,
    # top-level weights (must sum to 1):
    mandatory_weight=0.5,
    preferred_weight=0.5,
    # subcategory weights (must sum to 1):
    skills_weight=0.2,
    education_weight=0.2,
    background_weight=0.2,
    credentials_weight=0.2,
    responsibilities_weight=0.2,
):
    """
    For each job_id in `job_scores_dict`, compute:
      overall_mandatory,
      overall_preferred,
      overall_score,
      overall_skills, overall_education, overall_background, overall_credentials

    Then return a list of tuples (job_id, final_score_dict), sorted by "overall_score"
    descending.

    Weighted-sum logic:
      - If a sub-score is None, skip it (do not treat as 0).
      - If all sub-scores for "mandatory" are None => overall_mandatory is None; similarly for "preferred".
      - overall_score is a weighted average of overall_mandatory & overall_preferred, ignoring None.

    We also enforce:
      mandatory_weight + preferred_weight == 1
      skills_weight + education_weight + background_weight + credentials_weight + responsibilities_weight == 1
    """

    import math

    # Check top-level weights
    eps = 1e-9
    if abs((mandatory_weight + preferred_weight) - 1.0) > eps:
        raise ValueError("Error: mandatory_weight + preferred_weight must equal 1.")
    # Check subcategory weights
    subcat_sum = (
        skills_weight
        + education_weight
        + background_weight
        + credentials_weight
        + responsibilities_weight
    )
    if abs(subcat_sum - 1.0) > eps:
        raise ValueError("Error: subcategory weights must sum to 1.")

    def safe_avg(vals):
        """Average ignoring None."""
        v = [x for x in vals if x is not None]
        return sum(v) / len(v) if v else None

    def weighted_avg(subscores: dict, weights: dict):
        """
        subcategory-based weighted average ignoring None.
        e.g. subscores = {"skill": 0.8, "education": None, "background": 0.9, ...}
             weights    = {"skill": 0.2, "education": 0.2, "background": 0.2, ...}

        Sums only the sub-scores that are not None.
        If all are None => None.
        """
        numerator = 0.0
        denom = 0.0
        for cat, val in subscores.items():
            if val is not None:
                w = weights.get(cat, 0.0)
                numerator += val * w
                denom += w
        if denom == 0.0:
            return None
        return numerator / denom

    results = {}

    for job_id, data in job_scores_dict.items():
        # Extract mandatory sub-scores
        m_skill = data.get("mandatory_skill_score")
        m_edu = data.get("mandatory_education_score")
        m_bg = data.get("mandatory_background_score")
        m_cred = data.get("mandatory_credentials_score")
        m_resp = data.get("responsibilities_score")  # single responsibilities

        mandatory_subscores = {
            "skill": m_skill,
            "education": m_edu,
            "background": m_bg,
            "credentials": m_cred,
            "responsibilities": m_resp,
        }
        mandatory_weights = {
            "skill": skills_weight,
            "education": education_weight,
            "background": background_weight,
            "credentials": credentials_weight,
            "responsibilities": responsibilities_weight,
        }
        overall_mandatory = weighted_avg(mandatory_subscores, mandatory_weights)

        # Extract preferred sub-scores
        p_skill = data.get("preferred_skill_score")
        p_edu = data.get("preferred_education_score")
        p_bg = data.get("preferred_background_score")
        p_cred = data.get("preferred_credentials_score")
        # No responsibilities for preferred
        preferred_subscores = {
            "skill": p_skill,
            "education": p_edu,
            "background": p_bg,
            "credentials": p_cred,
        }
        preferred_weights = {
            "skill": skills_weight,
            "education": education_weight,
            "background": background_weight,
            "credentials": credentials_weight,
        }
        overall_preferred = weighted_avg(preferred_subscores, preferred_weights)

        # Combine top-level with mandatory/preferred weighting
        # skipping any that is None
        top_pairs = []
        if overall_mandatory is not None:
            top_pairs.append((overall_mandatory, mandatory_weight))
        if overall_preferred is not None:
            top_pairs.append((overall_preferred, preferred_weight))
        if not top_pairs:
            final_score = None
        else:
            sum_w = sum(w for _, w in top_pairs)
            final_score = sum(s * w for s, w in top_pairs) / sum_w

        # Category-level averages ignoring None
        # (like overall_skills, overall_education, etc.)
        ms = data.get("mandatory_skill_score")
        ps = data.get("preferred_skill_score")
        overall_skills = safe_avg([ms, ps])

        me = data.get("mandatory_education_score")
        pe = data.get("preferred_education_score")
        overall_education = safe_avg([me, pe])

        mb = data.get("mandatory_background_score")
        pb = data.get("preferred_background_score")
        overall_background = safe_avg([mb, pb])

        mc = data.get("mandatory_credentials_score")
        pc = data.get("preferred_credentials_score")
        overall_credentials = safe_avg([mc, pc])

        # Build final record for this job
        new_data = dict(data)  # copy original fields
        new_data.update(
            {
                "overall_mandatory": overall_mandatory,
                "overall_preferred": overall_preferred,
                "overall_score": final_score,
                "overall_skills": overall_skills,
                "overall_education": overall_education,
                "overall_background": overall_background,
                "overall_credentials": overall_credentials,
            }
        )
        results[job_id] = new_data

    # Now we build a list of (job_id, final_scores), sorted descending by "overall_score".
    # If "overall_score" is None, treat it as 0 for sorting.
    sorted_list = sorted(
        results.items(), key=lambda x: x[1].get("overall_score") or 0.0, reverse=True
    )

    return sorted_list
