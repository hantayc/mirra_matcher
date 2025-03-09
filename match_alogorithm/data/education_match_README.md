# Education Matching Code Documentation

This document provides a detailed description of the code's functionality, organized by function. Each section covers the purpose, inputs, processing flow, and outputs for the respective function. The documentation also outlines how the functions interact to compute the overall education match score.

---

## Global Constant

- **EDU_RANK**  
  A dictionary that maps various education level strings (including variants like different apostrophe forms) to a numeric rank.  
  This ranking is used to determine if a candidate’s education meets the minimum required level.

---

## Functions

### extract_job_education_requirements

- **Purpose:**  
  Extracts the education requirements from a job description JSON, distinguishing between _mandatory_ and _preferred_ education requirements.

- **Input:**  
  - `job_desc_json`: A JSON object representing the job description.

- **Flow:**  
  - Reads the `"mandatory"` and `"preferred"` sections of the JSON.
  - Extracts the list of education requirements under each section using the key `"education"`.

- **Output:**  
  Returns a tuple `(mandatory_edu, preferred_edu)` where each is a list of education requirement dictionaries.

---

### extract_resume_education

- **Purpose:**  
  Retrieves the education information from a candidate’s resume JSON.

- **Input:**  
  - `resume_json`: A JSON object representing the candidate's resume.

- **Flow:**  
  - Directly accesses the `"education"` key from the resume.

- **Output:**  
  Returns a list of education entries.

---

### extract_professional_background

- **Purpose:**  
  Extracts the candidate’s professional background information (e.g., job history, fields of study inferred from experience).

- **Input:**  
  - `resume_json`: The candidate’s resume JSON.

- **Flow:**  
  - Directly accesses the `"professional_background"` key from the resume.

- **Output:**  
  Returns a list of professional background entries.

---

### canidate_has_education_level

- **Purpose:**  
  Checks if the candidate’s education history meets or exceeds a required education rank.

- **Input:**  
  - `resume_education`: List of candidate education entries.
  - `required_rank`: A numeric value representing the minimum acceptable education level (as defined in **EDU_RANK**).

- **Flow:**  
  - Iterates over each education entry in the candidate’s education.
  - Retrieves the candidate’s education level string and maps it to a numeric rank using **EDU_RANK**.
  - Compares the candidate’s rank to the required rank.
  - Logs debug messages about the check.

- **Output:**  
  Returns `True` if any candidate education entry has a rank equal to or higher than the required rank; otherwise, returns `False`.

---

### get_equivalent_experience_score

- **Purpose:**  
  Computes a weighted average similarity score based on the candidate’s professional experience when formal education does not provide a match.  
  It uses inferred “field_of_study” values from the candidate’s experience.

- **Input:**  
  - `resume_experience`: List of candidate’s professional background entries.
  - `field_of_study_list`: List of required fields of study (strings) to compare against.
  - `threshold` (default `0.6`): Minimum similarity score to consider a match.
  - `min_years` (default `4`): Minimum cumulative years of relevant experience needed to compute a score.

- **Flow:**  
  - For each experience entry:
    - Retrieves the candidate’s list of inferred fields and job titles.
    - For each candidate field and each required field:
      - Computes a similarity score using an external function `nlp_similarity`.
      - If the similarity score meets or exceeds the threshold, it multiplies the similarity score by the years of experience for that entry.
      - Adds the product to a running sum and accumulates the total relevant years.
    - Uses a `break` to avoid checking further required fields once a match is found for a given candidate field.
  - If the candidate has accumulated at least `min_years` of relevant experience, the function calculates a weighted average score:
    ```
    weighted_avg = sum(similarity * years) / sum(years)
    ```
  - Logs detailed debug output throughout the process.

- **Output:**  
  Returns the weighted average similarity score if the total relevant experience meets the minimum; otherwise, returns `0.0`.

---

### get_required_field_score

- **Purpose:**  
  Computes an average similarity score for matching the candidate’s formal education against the required fields of study.  
  If no formal match is found and fallback is allowed, it uses the experience score.

- **Input:**  
  - `resume_education`: List of candidate’s education entries.
  - `resume_experience`: List of candidate’s professional background entries.
  - `required_fields`: List of required fields of study to match against.
  - `must_have_formal_degree`: Boolean flag indicating whether a formal degree match is mandatory.
  - `required_rank`: The numeric education level required.
  - `threshold` (default `0.6`): Minimum similarity score to accept a formal education match.
  - `min_years` (default `4`): Minimum required years of relevant experience if falling back.

- **Flow:**  
  - Iterates over each education entry:
    - Retrieves the candidate’s education level and maps it to a rank.
    - If the candidate’s education level meets the required rank:
      - Iterates through each major in the education entry.
      - For each major and each required field, calculates a similarity score.
      - If the score meets or exceeds the threshold, appends the score to a list.
  - If one or more formal matches are found:
    - Averages the collected similarity scores and returns that as the formal education score.
  - If no formal match is found:
    - Logs the lack of a formal match and calls **get_equivalent_experience_score** as a fallback.

- **Output:**  
  Returns either the average formal education similarity score or the fallback experience-based score.

---

### meets_education_requirement

- **Purpose:**  
  Evaluates a single education requirement and produces a match score.  
  It integrates both formal education matching and, optionally, professional experience fallback.

- **Input:**  
  - `requirement_dict`: Dictionary containing the education requirement (including keys like `"field_of_study"` and `"education_level"`).
  - `resume_education`: List of candidate’s education entries.
  - `resume_experience`: List of candidate’s professional background entries.
  - `threshold` (default `0.6`): Similarity threshold used for matching.
  - `min_years` (default `4`): Minimum required years of experience for fallback.
  - `allow_fallback` (default `False`): If `True`, allows the use of professional experience even if formal education does not meet the requirement.

- **Flow:**  
  - Extracts the list of required fields (`field_of_study`) and required education levels from the requirement.
  - Determines if a formal degree is strictly required by checking if any education level string contains `"or experience"`.  
    Also, if `allow_fallback` is `True`, experience fallback is allowed.
  - Computes the maximum required rank based on the education level strings using **EDU_RANK**.
  - If the requirement specifies a field of study:
    - Calls **get_required_field_score** to compute a score based on formal education (with possible fallback to experience).
  - If no specific field is provided:
    - Uses **canidate_has_education_level** to check if the candidate meets the minimum education rank.
    - If a formal degree is required and the candidate meets the rank, returns a perfect score (1.0); otherwise, returns 0.0.
    - If fallback is allowed and the candidate does not meet the formal requirement, falls back to computing an experience score via **get_equivalent_experience_score**.

- **Output:**  
  Returns a numeric score (similarity score or 0.0) representing how well the candidate meets this specific education requirement.

---

### calculate_education_match_score

- **Purpose:**  
  Computes the overall education match score for a candidate based on the job’s education requirements and the candidate’s resume.  
  It handles both mandatory and preferred education requirements.

- **Input:**  
  - `job_desc_json`: JSON object containing the job description.
  - `resume_json`: The candidate’s resume JSON.
  - `threshold` (default `0.7`): Similarity threshold for matching.
  - `min_years` (default `4`): Minimum required years of relevant experience for fallback evaluation.

- **Flow:**  
  - Calls **extract_job_education_requirements** to obtain mandatory and preferred education requirements.
  - Retrieves candidate details by calling **extract_resume_education** and **extract_professional_background**.
  - **Mandatory Requirements:**
    - Iterates over each mandatory education requirement.
    - For each, calls **meets_education_requirement**.
    - If any mandatory requirement returns a score of 0, the function immediately returns 0.0 (indicating failure to meet critical criteria).
    - Otherwise, averages the scores from all mandatory requirements.
  - **Preferred Requirements:**
    - Iterates over each preferred education requirement.
    - Calls **meets_education_requirement** with `allow_fallback=True` to allow experience-based fallback.
    - Averages the scores from all preferred requirements.
  - **Final Score:**
    - Combines the mandatory and preferred scores by averaging them (if both are present) or using whichever set is available.
  - Logs the overall match score.

- **Output:**  
  Returns a final overall education match score as a numeric value, representing the degree of match between the candidate’s education/experience and the job requirements.

---

## Summary of Flows and Interactions

1. **Data Extraction:**  
   - **extract_job_education_requirements**, **extract_resume_education**, and **extract_professional_background** extract relevant portions from the job and resume JSONs.

2. **Formal Education Check:**  
   - **canidate_has_education_level** and **get_required_field_score** evaluate if the candidate’s formal education meets the required levels and fields of study.
   - **get_required_field_score** uses `nlp_similarity` to compute a match score based on the candidate's majors.

3. **Experience Fallback:**  
   - **get_equivalent_experience_score** computes a weighted score based on relevant professional experience.
   - **meets_education_requirement** determines whether to use the formal education score or fall back to the experience-based score based on requirement flags.

4. **Overall Matching:**  
   - **calculate_education_match_score** integrates the results from mandatory and preferred requirement evaluations to generate an overall match score.

This completes the documentation of the education matching code.