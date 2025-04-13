from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from pinecone import Pinecone

# Imports
from match_alogorithm.utils.mandatory_skill_score import calculate_mandatory_skill_scores
from match_alogorithm.utils.preferred_skill_score import calculate_preferred_skill_scores
from match_alogorithm.utils.responsibilities_match_score import calculate_responsibilities_scores
from match_alogorithm.utils.mandatory_education_score import calculate_mandatory_education_scores
from match_alogorithm.utils.preferred_education_score import calculate_preferred_education_scores
from match_alogorithm.utils.mandatory_credentials_score import calculate_mandatory_credentials_scores
from match_alogorithm.utils.preferred_credentials_score import calculate_preferred_credentials_scores
from match_alogorithm.utils.mandatory_background_score import calculate_mandatory_background_scores
from match_alogorithm.utils.preferred_background_score import calculate_preferred_background_scores
from match_alogorithm.utils.merge_scores import merge_scores_by_job_id
from match_alogorithm.utils.overall_scores import make_overall_scores


###############################################################################
# Helper: Split a list into n roughly equal chunks
###############################################################################
def chunk_list(lst, n):
    """Splits lst into n roughly even chunks."""
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

###############################################################################
# Helper: Process Stage 2 for a chunk of job descriptions
###############################################################################
def process_stage2(job_chunk, candidate_resume_JSON):
    """
    For the given chunk of job descriptions, calculate the three Stage 2 scores,
    then merge them into a single dictionary.
    """
    responsibilities_score = calculate_responsibilities_scores(
        job_json_list=job_chunk, resume_json=candidate_resume_JSON
    )
    mandatory_skills_scores = calculate_mandatory_skill_scores(
        job_json_list=job_chunk, resume_json=candidate_resume_JSON
    )
    preferred_skills_scores = calculate_preferred_skill_scores(
        job_json_list=job_chunk, resume_json=candidate_resume_JSON
    )
    # Merge the three sets of scores for this chunk.
    merged_chunk = merge_scores_by_job_id(
        responsibilities_score,
        mandatory_skills_scores,
        preferred_skills_scores,
        filter=True,
        threshold=0.5,
    )
    return merged_chunk

###############################################################################
# Main Function: Calculate Match Score
###############################################################################
def calculate_match_score(job_desc_json_lst, candidate_resume_JSON, parallel_processing=True):
    """
    Calculates match scores.
    
    Stage 1: Calculate component scores (6 tasks) in parallel (if enabled).
    Stage 1.5: Merge and filter Stage 1 scores.
    Stage 2: Break up the job list into 10 chunks and compute additional dimension scores
             (responsibilities, mandatory skills, preferred skills) in parallel.
    Stage 2.5: Merge the Stage 2 results.
    Stage 3: Compute final overall scores and attach them to each job.
    """
    print("[calculate_match_score] START")

    print(f"[calculate_match_score] Total Length of Sample: {len(job_desc_json_lst)}")
    print(f"[calculate_match_score] parallel_processing={parallel_processing}")

    # Test Pinecone connection
    PINECONE_API_KEY = (
        "pcsk_7VkStS_ifR3SH9d1MSkkju9kP7DUt5M16CpNyzi9dwNBm7iUqyXmbKZWQbC55ZzfSEaAB"
    )
    PINECONE_ENVIRONMENT = "us-east-1"
    PINECONE_INDEX_NAME = "sample-100-strings"  # Must match an existing index or be created
    
    try:
        # Instantiate Pinecone client and get the index
        pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        pinecone_index = pc.Index(PINECONE_INDEX_NAME)
        print("Pinecone connected successfully!")
    except Exception as e:
        # If any error occurs, print it and fallback to None
        print("Error connecting to Pinecone, proceeding without it:", str(e))
        pc = None
        pinecone_index = None

    # ================================================================
    # Stage 1: Calculate component scores (6 tasks)
    # ================================================================
    print("[calculate_match_score] Stage 1: Start")
    if parallel_processing:
        print("[calculate_match_score] Stage 1: Submitting tasks to ThreadPoolExecutor...")
        with ThreadPoolExecutor() as executor:
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
            print("[calculate_match_score] Stage 1: Waiting for all futures...")
            mandatory_credentials_scores = futures_stage1["mandatory_credentials"].result()
            print("[calculate_match_score] Got mandatory_credentials_scores")
            preferred_credentials_scores = futures_stage1["preferred_credentials"].result()
            print("[calculate_match_score] Got preferred_credentials_scores")
            mandatory_education_scores = futures_stage1["mandatory_education"].result()
            print("[calculate_match_score] Got mandatory_education_scores")
            preferred_education_scores = futures_stage1["preferred_education"].result()
            print("[calculate_match_score] Got preferred_education_scores")
            mandatory_background_scores = futures_stage1["mandatory_background"].result()
            print("[calculate_match_score] Got mandatory_background_scores")
            preferred_background_scores = futures_stage1["preferred_background"].result()
            print("[calculate_match_score] Got preferred_background_scores")
    else:
        print("[calculate_match_score] Stage 1: Running tasks line by line...")
        mandatory_credentials_scores = calculate_mandatory_credentials_scores(
            job_desc_json_lst, candidate_resume_JSON
        )
        print("[calculate_match_score] Finished mandatory_credentials_scores")
        preferred_credentials_scores = calculate_preferred_credentials_scores(
            job_desc_json_lst, candidate_resume_JSON
        )
        print("[calculate_match_score] Finished preferred_credentials_scores")
        mandatory_education_scores = calculate_mandatory_education_scores(
            job_desc_json_lst, candidate_resume_JSON
        )
        print("[calculate_match_score] Finished mandatory_education_scores")
        preferred_education_scores = calculate_preferred_education_scores(
            job_desc_json_lst, candidate_resume_JSON
        )
        print("[calculate_match_score] Finished preferred_education_scores")
        mandatory_background_scores = calculate_mandatory_background_scores(
            job_desc_json_lst, candidate_resume_JSON
        )
        print("[calculate_match_score] Finished mandatory_background_scores")
        preferred_background_scores = calculate_preferred_background_scores(
            job_desc_json_lst, candidate_resume_JSON
        )
        print("[calculate_match_score] Finished preferred_background_scores")

    print("[calculate_match_score] Stage 1 complete. Merging results...")
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
    print("[calculate_match_score] Stage 1.5: Merged scores from Stage 1")

    # Filter the job list to only those that passed Stage 1.
    stage_job_desc_json_lst = [
        job for job in job_desc_json_lst if job.get("job_id") in set(stage1_scores.keys())
    ]
    print(f"[calculate_match_score] Total Length after Stage 1: {len(stage_job_desc_json_lst)}")

    # ================================================================
    # Stage 2: Additional dimension scoring (3 tasks)
    # ================================================================
    print("[calculate_match_score] Stage 2: Start")
    if parallel_processing:
        print("[calculate_match_score] Stage 2: Splitting jobs into 10 chunks and submitting tasks...")
        num_chunks = 10
        job_chunks = chunk_list(stage_job_desc_json_lst, num_chunks)
        with ThreadPoolExecutor(max_workers=num_chunks) as executor:
            futures_stage2 = [
                executor.submit(process_stage2, chunk, candidate_resume_JSON)
                for chunk in job_chunks
            ]
            print("[calculate_match_score] Stage 2: Waiting for all futures...")
            results_list = [f.result() for f in futures_stage2]
    else:
        print("[calculate_match_score] Stage 2: Running tasks line by line...")
        responsibilities_score = calculate_responsibilities_scores(
            job_json_list=stage_job_desc_json_lst, resume_json=candidate_resume_JSON
        )
        print("[calculate_match_score] Finished responsibilities_score")
        mandatory_skills_scores = calculate_mandatory_skill_scores(
            job_json_list=stage_job_desc_json_lst, resume_json=candidate_resume_JSON
        )
        print("[calculate_match_score] Finished mandatory_skills_scores")
        preferred_skills_scores = calculate_preferred_skill_scores(
            job_json_list=stage_job_desc_json_lst, resume_json=candidate_resume_JSON
        )
        print("[calculate_match_score] Finished preferred_skills_scores")
        results_list = [
            merge_scores_by_job_id(
                responsibilities_score,
                mandatory_skills_scores,
                preferred_skills_scores,
                filter=True,
                threshold=0.5,
            )
        ]

    # Merge all Stage 2 chunk results into one dictionary.
    stage2_scores = reduce(
        lambda a, b: merge_scores_by_job_id(a, b, filter=True, threshold=0.5),
        results_list,
    )
    print("[calculate_match_score] Stage 2.5: Merged scores from Stage 2")

    final_job_desc_json_lst = [
        job for job in stage_job_desc_json_lst if job.get("job_id") in stage2_scores
    ]
    print(f"[calculate_match_score] Total Length after Stage 2: {len(final_job_desc_json_lst)}")

    # ================================================================
    # Stage 3: Final overall score calculation
    # ================================================================
    print("[calculate_match_score] Stage 3: Computing overall scores...")
    overall_scores = make_overall_scores(stage2_scores)
    overall_scores = dict(overall_scores)

    print("[calculate_match_score] Attaching match_scores to each job...")
    match_results = []
    for job in final_job_desc_json_lst:
        job_id = job.get("job_id")
        print(f"[calculate_match_score] Processing job_id: {job_id}")
        if job_id in overall_scores:
            job["match_scores"] = overall_scores[job_id]
            match_results.append(job)
            print(f"[calculate_match_score] Attached match_scores for job_id: {job_id}")

    print("[calculate_match_score] Sorting results by overall match score...")
    match_results = sorted(
        match_results,
        key=lambda x: x.get("match_scores", {}).get("overall_score", 0),
        reverse=True,
    )

    print("[calculate_match_score] DONE. Returning results.")
    return match_results

###############################################################################
# MAIN
###############################################################################
if __name__ == "__main__":
    # Example usage: replace with your actual data.
    job_desc_json_lst = []  # List of job description JSON objects with "job_id"
    candidate_resume_JSON = {}  # Candidate resume JSON object

    results = calculate_match_score(job_desc_json_lst, candidate_resume_JSON, parallel_processing=True)
    print("Final Results:")
    print(results)