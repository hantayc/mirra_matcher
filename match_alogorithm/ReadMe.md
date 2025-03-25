# Matching Algorithm for Job Descriptions and Resumes

This project implements a matching algorithm that uses natural language processing (NLP) techniques to evaluate how well candidate resumes match job descriptions. The matching covers multiple categories including skills, education, professional background (role/industry), responsibilities, and credentials.

The algorithm leverages pre-trained sentence transformers to compute semantic similarity scores between candidate and job description elements, and then aggregates these scores into overall match scores.

## Directory Structure
```
.
├── ReadMe.md
├── archive
│   ├── job_description.txt
│   ├── matching_algo.ipynb
│   ├── metadata_append_json.ipynb
│   ├── ref_job.txt
│   ├── resume_json.txt
│   ├── skills wrapper function.ipynb
│   └── test.txt
├── data
│   ├── dhi_skills_broader.txt
│   ├── dhi_skills_broader_transitive.txt
│   ├── education_match_README.md
│   ├── sample_des_extractions_test_final_3.22.25.xlsx
│   └── sample_res_extractions_final_3.18.25.xlsx
├── individual_match_score_fn_test.ipynb
└── utils
├── init.py
├── load_embedding_fn.py         # Loads a sentence transformer model and moves it to GPU (if available)
├── semantic_similarity.py         # Contains functions to compute cosine similarity and normalized semantic similarity with caching.
├── safe_averages.py               # Provides helper(s) such as safe_average for averaging scores safely.
├── mandatory_skill_score.py       # Functions for extracting job/resume skill data and computing mandatory skill match scores.
├── preferred_skill_score.py       # Functions for computing preferred skill match scores.
├── mandatory_education_score.py   # Functions for extracting education requirements and computing mandatory education match scores.
├── preferred_education_score.py   # Functions for computing preferred education match scores.
├── mandatory_background_score.py  # Functions for computing professional background (role) and industry match scores for mandatory requirements.
├── preferred_background_score.py  # Functions for computing background and industry scores for preferred requirements.
├── mandatory_credentials_score.py # Functions for computing mandatory credentials match scores.
├── preferred_credentials_score.py # Functions for computing preferred credentials match scores.
├── responsibilities_match_score.py# Functions for computing responsibilities match scores.
├── merge_scores.py                # Functions for merging score dictionaries by job_id.
├── overall_scores.py              # Aggregates scores from all sections (skills, education, responsibilities, credentials, background) into overall match scores.
```
## Project Overview

The matching algorithm is designed to compare a candidate’s resume (in JSON format) to a job description (also in JSON format) across multiple dimensions:

1. **Skills Matching**  
   - **Mandatory and Preferred Skills:**  
     The algorithm extracts required skills from the job description and candidate skills from the resume. It computes semantic similarity between candidate skill terms and job-required skill terms.  
   - **Usage:**  
     Use `calculate_mandatory_skill_score()` and `calculate_preferred_skill_score()` to compute scores for each category; then merge with `calculate_overall_skill_match_score()`.

2. **Education Matching**  
   - **Mandatory and Preferred Education:**  
     The algorithm compares candidate education (degree level and fields of study) with job education requirements. It uses both formal education matching (based on candidate’s majors) and an experience fallback if allowed.  
   - **Usage:**  
     Functions such as `calculate_mandatory_education_score()` and `calculate_preferred_education_score()` compute the scores. The overall education score is available via `calculate_overall_education_match_score()`.

3. **Professional Background Matching**  
   - **Background (Role) and Industry:**  
     The algorithm evaluates how well a candidate’s professional background (job roles) and industry experience match the job’s requirements. It supports a special “Work Experience” mode that only checks total years of experience.
   - **Usage:**  
     Use `calculate_mandatory_background_score()` and `calculate_preferred_background_score()` to compute background and industry scores, and then combine them via `calculate_overall_background_score()`.
     
4. **Responsibilities Matching**  
   - **Job Responsibilities:**  
     The system compares candidate responsibilities (extracted from their skills) against the job’s responsibilities to compute a match score.
   - **Usage:**  
     `calculate_overall_responsibilities_match_score()` returns the responsibilities match score for a job.

5. **Credentials Matching**  
   - **Mandatory and Preferred Credentials:**  
     The algorithm compares candidate credentials with job-required credentials using semantic similarity.
   - **Usage:**  
     Functions `calculate_mandatory_credentials_score()` and `calculate_preferred_credentials_score()` compute these scores. An overall credential score is available via `calculate_overall_credentials_score()`.

6. **Overall Aggregation**  
   - **Merge and Overall Score:**  
     The overall match score is computed by merging the scores from each section (skills, education, responsibilities, credentials, background) using weighted averages.  
   - **Usage:**  
     The function `calculate_overall_match_score()` in `overall_scores.py` collects all section scores (ignoring sections with no requirements by returning `None`) and computes a final overall score.  
     Additionally, the `merge_scores.py` module provides a helper to merge score dictionaries (keyed by job_id) across various sections.

## How to Use the Functions

### Setting Up

1. **Install Dependencies:**  
   Ensure you have installed the required Python packages (e.g., `pandas`, `numpy`, `sentence-transformers`).

2. **Data Files:**  
   Place your job description and resume data (for example, Excel files) in the `data` folder.

3. **Running the Notebook:**  
   You can test individual functions using the provided Jupyter notebooks (e.g., `individual_match_score_fn_test.ipynb`).

### Example Usage

Below is an example of how to compute and merge scores:

```python
from utils.mandatory_skill_score import calculate_mandatory_skill_score
from utils.preferred_skill_score import calculate_preferred_skill_score
from utils.merge_scores import merge_scores_by_job_id
from utils.overall_scores import calculate_overall_match_score

# Assume job_desc_json is a list/Series of job description JSON objects,
# and resume_json is a resume JSON object.

# Compute mandatory and preferred skill scores separately.
mandatory_skill_scores = {}
preferred_skill_scores = {}

for job in job_desc_json:
    job_id = job.get("job_id")
    mandatory_skill_scores[job_id] = calculate_mandatory_skill_score(job, resume_json)
    preferred_skill_scores[job_id] = calculate_preferred_skill_score(job, resume_json)

# Merge all scores into one dictionary (other sections are computed similarly)
final_overall_scores = calculate_overall_match_score(job_json=job, resume_json=resume_json)
print(final_overall_scores)