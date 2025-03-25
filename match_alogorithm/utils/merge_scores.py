def merge_scores_by_job_id(*score_dicts, filter=False, threshold=0.0):
    """
    Merges multiple dictionaries (whose keys are job_ids and values are dictionaries
    of scores) into a single dictionary keyed by job_id.

    If filter=True, then after merging, for each job_id we look through every field:
      - If any field is numeric (int/float), not None, and < threshold,
        we remove that entire job_id from the final output.

    None scores never cause a filter-out, and non-numeric fields are ignored.

    Example:
      merged = merge_scores_by_job_id(
          mandatory_background_scores,
          preferred_background_scores,
          filter=True, threshold=0.5
      )
      # If a single numeric field under a job_id is e.g. 0.3, remove that job_id entirely.
    """

    # 1) Merge everything first
    merged = {}
    for d in score_dicts:
        if d is None:
            continue  # Skip dictionaries that are None.
        for job_id, score_info in d.items():
            if job_id not in merged:
                merged[job_id] = {}
            if score_info is not None and isinstance(score_info, dict):
                merged[job_id].update(score_info)

    # 2) If filter=False, just return as is
    if not filter:
        return merged

    # 3) Filter out job_ids with any numeric field below threshold
    #    We'll gather job_ids_to_remove and then remove them in one go
    job_ids_to_remove = []

    for job_id, score_dict in merged.items():
        # Score dict might have multiple fields
        # If any numeric field is < threshold => remove job_id
        remove_this_job = False
        for field_name, value in score_dict.items():
            if (
                value is not None
                and isinstance(value, (int, float))
                and value < threshold
            ):
                remove_this_job = True
                break
        if remove_this_job:
            job_ids_to_remove.append(job_id)

    # Remove them
    for job_id in job_ids_to_remove:
        del merged[job_id]

    return merged
