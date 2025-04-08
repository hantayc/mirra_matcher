import math
from match_alogorithm.utils.semantic_similarity import nlp_similarity_cached


def safe_average(values):
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def extract_job_mandatory_skills(job_json):
    return job_json.get("mandatory", {}).get("hard_skills", [])


def extract_resume_skills(resume_json):
    return resume_json.get("skills", [])


def compute_group_similarity(candidate_group, required_group):
    """
    For a multi-term required_group (e.g. ["Salesforce dev", "Apex"]),
    find the best match for each required term among candidate_group,
    then average those best matches.
    """
    if not candidate_group or not required_group:
        return 0.0

    sims_for_required_terms = []
    for req_term in required_group:
        best_for_req_term = 0.0
        for cand_term in candidate_group:
            sim = nlp_similarity_cached(cand_term, req_term)
            if sim > best_for_req_term:
                best_for_req_term = sim
        sims_for_required_terms.append(best_for_req_term)
    return sum(sims_for_required_terms) / len(sims_for_required_terms)


def compute_required_skill_similarity(candidate_skill_item, job_required_skill):
    """
    Each job_required_skill can be a list of multiple sub-groups
    e.g. [ ["Salesforce dev","Apex"], ["Salesforce.com development","Apex"] ].
    We find the best among them.
    """
    if not job_required_skill:
        return 0.0

    # If the job_required_skill is a single group, wrap it for uniform iteration
    if isinstance(job_required_skill[0], str):
        job_required_skill = [job_required_skill]

    candidate_group = candidate_skill_item.get("skill", [])
    if not candidate_group:
        return 0.0

    best_sim = 0.0
    for req_group in job_required_skill:
        sim_score = compute_group_similarity(candidate_group, req_group)
        if sim_score > best_sim:
            best_sim = sim_score
    return best_sim


def aggregate_best_entries(resume_skills, job_required_skill):
    """
    Returns a list of dicts, each dict having:
        {
          "job_id": ...,
          "sim": <best similarity for that job_id>,
          "years": <max years for that job_id>
        }

    We do NOT sum multiple lines from the same job_id; we take whichever line
    has the highest similarity, and whichever has the maximum years, for that job_id.
    """
    # Temporary map of job_id -> {"sim": float, "years": float}
    by_job_id = {}

    for cand_skill_item in resume_skills:
        jbid = cand_skill_item.get("job_id", "")
        cand_years = cand_skill_item.get("years", 0.0)
        sim = compute_required_skill_similarity(cand_skill_item, job_required_skill)

        if jbid not in by_job_id:
            by_job_id[jbid] = {"sim": sim, "years": cand_years}
        else:
            if sim > by_job_id[jbid]["sim"]:
                by_job_id[jbid]["sim"] = sim
            if cand_years > by_job_id[jbid]["years"]:
                by_job_id[jbid]["years"] = cand_years

    # Convert to a list
    result = []
    for jbid, vals in by_job_id.items():
        # Only keep if similarity > 0
        if vals["sim"] > 0.0:
            result.append({"job_id": jbid, "sim": vals["sim"], "years": vals["years"]})
    return result


def compute_single_requirement_score(
    resume_skills, job_required_skill, min_years_required
):
    """
    Core function that:

    1) Aggregates the best similarity & max years per job_id.
    2) Sorts them by similarity desc.
    3) Iterates in descending similarity order:
       a) If coverageUsed=0 and we encounter an empty job_id skill:
          - If it alone meets min_years_required => done
          - Else skip it
       b) If coverageUsed=0 and we encounter a real job_id skill => start summation from real job_ids
          until min_years_required is met or exhausted
       c) Once we pick coverage from empty or real, we do NOT mix them.

    Returns the final weighted similarity score for this requirement.
    """
    print("\n=== Processing Single Skill Requirement ===")
    print(f"Required skill: {job_required_skill}")
    print(f"Min years required: {min_years_required}")

    if not resume_skills or not job_required_skill:
        return 0.0

    # Gather best skill lines (one per job_id)
    best_entries = aggregate_best_entries(resume_skills, job_required_skill)

    if not best_entries:
        print("No nonzero similarity entries. Returning 0.0")
        return 0.0

    # Sort by similarity desc
    best_entries.sort(key=lambda x: x["sim"], reverse=True)

    coverage_used = 0.0
    weighted_sum = 0.0
    coverage_mode = None  # can be "real" or "empty"
    needed = float(min_years_required)

    print("\n-- Sorted Skill Entries (desc by sim) --")
    for i, e in enumerate(best_entries, 1):
        print(
            f" {i}) job_id='{e['job_id'] or '[EMPTY]'}', sim={e['sim']:.3f}, yrs={e['years']:.2f}"
        )

    # Now iterate in sorted order
    for item in best_entries:
        jbid = item["job_id"]
        sim = item["sim"]
        yrs = item["years"]

        if coverage_used >= min_years_required:
            print("Already met coverage. Break.")
            break

        # If we haven't chosen coverage yet (coverage_mode=None):
        if coverage_mode is None:
            if jbid.strip() == "":
                # It's an empty job_id skill
                if yrs >= min_years_required:
                    # Use it alone => done
                    fraction = min_years_required / float(min_years_required)
                    weighted_sum += sim * fraction
                    coverage_used += min_years_required
                    coverage_mode = "empty"
                    print(
                        f"Chose empty job_id skill alone: yrs={yrs}, sim={sim:.3f}, coverage_used={coverage_used:.2f}"
                    )
                    break
                else:
                    # Skip it, because it doesn't meet min years alone
                    print(
                        f"Skipping empty job_id skill with yrs={yrs}, sim={sim:.3f}, doesn't meet min_years={min_years_required}."
                    )
                    continue
            else:
                # It's a real job_id => start real coverage accumulation
                coverage_mode = "real"
                use_years = min(yrs, needed)
                fraction = use_years / float(min_years_required)
                weighted_sum += sim * fraction
                coverage_used += use_years
                needed -= use_years
                print(
                    f"Starting real coverage with job_id={jbid}, sim={sim:.3f}, used_yrs={use_years:.2f}, coverage_used={coverage_used:.2f}"
                )
        else:
            # We already picked a mode
            if coverage_mode == "empty":
                # We used an empty job_id skill that meets coverage alone => we won't accumulate more
                # So we just break or skip
                print(
                    "Already satisfied coverage with an empty job_id skill. Not adding more."
                )
                break
            else:
                # coverage_mode == "real"
                if jbid.strip() == "":
                    # skip empty job_id lines
                    print(
                        f"Skipping empty job_id skill because we already started real coverage: sim={sim:.3f}"
                    )
                    continue
                else:
                    # same coverage_mode=real => accumulate partial coverage
                    use_years = min(yrs, needed)
                    fraction = use_years / float(min_years_required)
                    weighted_sum += sim * fraction
                    coverage_used += use_years
                    needed -= use_years
                    print(
                        f"Continuing real coverage with job_id={jbid}, sim={sim:.3f}, used_yrs={use_years:.2f}, coverage_used={coverage_used:.2f}"
                    )

    # If coverage_used < min_years_required, that's partial coverage
    if coverage_used <= 0:
        print("No coverage used => 0.0 final.")
        return 0.0

    if coverage_used < min_years_required:
        # partial coverage scenario
        print(f"=> Partial coverage: used {coverage_used} out of {min_years_required}")
        # Usually weighted_sum is already scaled fractionally, so we can just return it
        return weighted_sum

    # coverage_used >= min_years_required => full coverage
    print(f"=> Full coverage. Weighted sum = {weighted_sum:.3f}")
    return weighted_sum


def calculate_skill_match_score(job_json, resume_json):
    """
    Iterates over each mandatory skill requirement in the job JSON,
    calls compute_single_requirement_score, and returns their average.
    """
    print("\n======================")
    print("BEGIN: calculate_skill_match_score")
    print("======================")

    job_skills = extract_job_mandatory_skills(job_json)
    if not job_skills:
        print("No mandatory skill requirements found. Returning None.")
        return None

    resume_skills = extract_resume_skills(resume_json)
    requirement_scores = []
    for idx, req in enumerate(job_skills, start=1):
        print(f"\n********** REQUIREMENT #{idx} **********")
        job_required_skill = req.get("skill", [])
        min_years_required = req.get("minyears", [0])[0]

        score_for_this_req = compute_single_requirement_score(
            resume_skills, job_required_skill, min_years_required
        )
        print(
            f"[REQUIREMENT #{idx}] Weighted Similarity Score = {score_for_this_req:.3f}"
        )
        requirement_scores.append(score_for_this_req)

    overall_skill = safe_average(requirement_scores)
    if overall_skill is None:
        print("No valid scores found at all. Returning None.")
        return None
    else:
        print(f"\n=> Overall Mandatory Skill Match Score = {overall_skill:.3f}")
        return overall_skill


def calculate_mandatory_skill_score(job_json, resume_json):
    score = calculate_skill_match_score(job_json, resume_json)
    return {"mandatory_skill_score": score}


def calculate_mandatory_skill_scores(job_json_list, resume_json):
    """
    Accepts a list of job JSON objects and returns a dictionary
    mapping each job's job_id to its mandatory skill score.
    """
    results = {}
    print("\n##################################")
    print("BEGIN: calculate_mandatory_skill_scores")
    print("##################################")

    for i, job_json in enumerate(job_json_list, start=1):
        job_id = job_json.get("job_id", f"job_{i}")
        print(f"\n======================")
        print(f"PROCESSING JOB_ID: {job_id}")
        print(f"======================")
        score_dict = calculate_mandatory_skill_score(job_json, resume_json)
        results[job_id] = score_dict

    print("\n########## FINAL RESULTS ##########")
    for k, v in results.items():
        print(f"  job_id = {k} => {v}")
    print("###################################")

    return results
