"""
job_chunker.py - Module for chunking job description JSON into text chunks for embedding.

Functions to convert structured job description JSON data into
human-readable text chunks suitable for semantic vector embedding.
"""

from typing import Dict, List, Any, Union
import re
import uuid

def chunk_job_description(job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a job description into chunks for embedding.
    
    Args:
        job_data: Job description dictionary with qualification data
        
    Returns:
        List of chunks, each with text and metadata
    """
    chunks = []
    
    # validate input
    if not isinstance(job_data, dict):
        raise ValueError("Job data must be a dictionary")
    
    # extract job ID (or generate one if not present)
    job_id = job_data.get("job_id")
    if not job_id:
        job_id = str(uuid.uuid4())
        job_data["job_id"] = job_id
    
    # process details section
    if "details" in job_data:
        # Extract job title as a chunk
        details = job_data["details"]
        if "job_title" in details and details["job_title"]:
            job_title_text = details["job_title"][0] if isinstance(details["job_title"], list) else details["job_title"]
            chunks.append({
                "text": f"Job title: {job_title_text}",
                "metadata": {
                    "source_type": "job_description",
                    "chunk_type": "job_title",
                    "job_id": job_id
                }
            })
        
        # extract employment type
        if "employment_type" in details and details["employment_type"]:
            employment_type = details["employment_type"][0] if isinstance(details["employment_type"], list) else details["employment_type"]
            chunks.append({
                "text": f"Employment type: {employment_type}",
                "metadata": {
                    "source_type": "job_description",
                    "chunk_type": "employment_type",
                    "job_id": job_id
                }
            })
        
        # extract wfh policy
        if "wfh_policy" in details and details["wfh_policy"]:
            wfh_policy = details["wfh_policy"][0] if isinstance(details["wfh_policy"], list) else details["wfh_policy"]
            chunks.append({
                "text": f"Work arrangement: {wfh_policy}",
                "metadata": {
                    "source_type": "job_description",
                    "chunk_type": "wfh_policy",
                    "job_id": job_id
                }
            })
        
        # extract experience level
        if "experience_level" in details and details["experience_level"]:
            exp_level = details["experience_level"][0] if isinstance(details["experience_level"], list) else details["experience_level"]
            chunks.append({
                "text": f"Experience level: {exp_level}",
                "metadata": {
                    "source_type": "job_description",
                    "chunk_type": "experience_level",
                    "job_id": job_id
                }
            })
    
    # process mandatory qualifications
    if "mandatory" in job_data:
        # Process hard skills
        if "hard_skills" in job_data["mandatory"]:
            for idx, skill in enumerate(job_data["mandatory"]["hard_skills"]):
                skill_text = create_text_from_skill(skill)
                if skill_text:
                    skill_name = extract_skill_name(skill)
                    minyears = extract_minyears(skill)
                    
                    chunks.append({
                        "text": f"Required skill: {skill_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "skill",
                            "requirement_level": "mandatory",
                            "job_id": job_id,
                            "skill_name": skill_name,
                            "minyears": minyears
                        }
                    })
        
        # process education
        if "education" in job_data["mandatory"]:
            for idx, edu in enumerate(job_data["mandatory"]["education"]):
                edu_text = create_text_from_education(edu)
                if edu_text:
                    chunks.append({
                        "text": f"Required education: {edu_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "education",
                            "requirement_level": "mandatory",
                            "job_id": job_id
                        }
                    })
        
        # process credentials
        if "credentials" in job_data["mandatory"]:
            for idx, cred in enumerate(job_data["mandatory"]["credentials"]):
                cred_text = create_text_from_credential(cred)
                if cred_text:
                    chunks.append({
                        "text": f"Required credential: {cred_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "credential",
                            "requirement_level": "mandatory",
                            "job_id": job_id
                        }
                    })
        
        # process professional background
        if "professional_background" in job_data["mandatory"]:
            for idx, bg in enumerate(job_data["mandatory"]["professional_background"]):
                bg_text = create_text_from_background(bg)
                if bg_text:
                    minyears = extract_background_years(bg)
                    chunks.append({
                        "text": f"Required experience: {bg_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "experience",
                            "requirement_level": "mandatory",
                            "job_id": job_id,
                            "minyears": minyears
                        }
                    })
    
    # process preferred qualifications
    if "preferred" in job_data:
        # Process hard skills
        if "hard_skills" in job_data["preferred"]:
            for idx, skill in enumerate(job_data["preferred"]["hard_skills"]):
                skill_text = create_text_from_skill(skill)
                if skill_text:
                    skill_name = extract_skill_name(skill)
                    minyears = extract_minyears(skill)
                    
                    chunks.append({
                        "text": f"Preferred skill: {skill_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "skill",
                            "requirement_level": "preferred",
                            "job_id": job_id,
                            "skill_name": skill_name,
                            "minyears": minyears
                        }
                    })
        
        # process education
        if "education" in job_data["preferred"]:
            for idx, edu in enumerate(job_data["preferred"]["education"]):
                edu_text = create_text_from_education(edu)
                if edu_text:
                    chunks.append({
                        "text": f"Preferred education: {edu_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "education",
                            "requirement_level": "preferred",
                            "job_id": job_id
                        }
                    })
        
        # process credentials
        if "credentials" in job_data["preferred"]:
            for idx, cred in enumerate(job_data["preferred"]["credentials"]):
                cred_text = create_text_from_credential(cred)
                if cred_text:
                    chunks.append({
                        "text": f"Preferred credential: {cred_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "credential",
                            "requirement_level": "preferred",
                            "job_id": job_id
                        }
                    })
        
        # process professional background
        if "professional_background" in job_data["preferred"]:
            for idx, bg in enumerate(job_data["preferred"]["professional_background"]):
                bg_text = create_text_from_background(bg)
                if bg_text:
                    minyears = extract_background_years(bg)
                    chunks.append({
                        "text": f"Preferred experience: {bg_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "experience",
                            "requirement_level": "preferred",
                            "job_id": job_id,
                            "minyears": minyears
                        }
                    })
    
    # process responsibilities
    if "responsibility" in job_data:
        # Process hard skills as responsibilities
        if "hard_skills" in job_data["responsibility"]:
            for idx, skill in enumerate(job_data["responsibility"]["hard_skills"]):
                skill_text = extract_skill_name(skill)
                if skill_text:
                    chunks.append({
                        "text": f"Job responsibility: {skill_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "responsibility",
                            "requirement_level": "responsibility",
                            "job_id": job_id
                        }
                    })
        
        # process professional background as responsibilities
        if "professional_background" in job_data["responsibility"]:
            for idx, bg in enumerate(job_data["responsibility"]["professional_background"]):
                bg_text = extract_background_text(bg)
                if bg_text:
                    chunks.append({
                        "text": f"Job responsibility: {bg_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "responsibility",
                            "requirement_level": "responsibility",
                            "job_id": job_id
                        }
                    })
    
    return chunks

def create_text_from_skill(skill_item: Dict[str, Any]) -> str:
    """
    Convert a skill item JSON into a human-readable text chunk.
    
    Args:
        skill_item: Dictionary with skill information
        
    Returns:
        Formatted skill text string
    """
    if not skill_item:
        return ""
    
    skill_text = extract_skill_name(skill_item)
    if not skill_text:
        return ""
    
    # Add years of experience if available
    minyears = extract_minyears(skill_item)
    if minyears and minyears > 0:
        year_word = "years" if minyears != 1 else "year"
        return f"{skill_text} with at least {minyears} {year_word} of experience"
    
    return skill_text

def extract_skill_name(skill_item: Dict[str, Any]) -> str:
    """Extract the skill name from a skill dictionary."""
    if not skill_item or "skill" not in skill_item:
        return ""
    
    if isinstance(skill_item["skill"], list) and skill_item["skill"]:
        return skill_item["skill"][0]
    elif isinstance(skill_item["skill"], str):
        return skill_item["skill"]
    
    return ""

def extract_minyears(skill_item: Dict[str, Any]) -> Union[int, float]:
    """Extract the minimum years from a skill or background dictionary."""
    if not skill_item or "minyears" not in skill_item:
        return 0
    
    if isinstance(skill_item["minyears"], list) and skill_item["minyears"]:
        try:
            return int(skill_item["minyears"][0])
        except (ValueError, TypeError):
            return 0
    elif isinstance(skill_item["minyears"], (int, float)):
        return skill_item["minyears"]
    
    return 0

def create_text_from_education(education_item: Dict[str, Any]) -> str:
    """
    Convert an education item JSON into a human-readable text chunk.
    
    Args:
        education_item: Dictionary with education information
        
    Returns:
        Formatted education text string
    """
    if not education_item:
        return ""
    
    # Extract education level
    education_level = ""
    if "education_level" in education_item and education_item["education_level"]:
        if isinstance(education_item["education_level"], list) and education_item["education_level"]:
            education_level = education_item["education_level"][0]
        elif isinstance(education_item["education_level"], str):
            education_level = education_item["education_level"]
    
    # Extract field of study
    field_of_study = ""
    if "field_of_study" in education_item and education_item["field_of_study"]:
        if isinstance(education_item["field_of_study"], list) and education_item["field_of_study"]:
            field_of_study = ", ".join(education_item["field_of_study"])
        elif isinstance(education_item["field_of_study"], str):
            field_of_study = education_item["field_of_study"]
    
    # Combine into a natural language statement
    if education_level and field_of_study:
        return f"{education_level} in {field_of_study}"
    elif education_level:
        return f"{education_level}"
    elif field_of_study:
        return f"Degree in {field_of_study}"
    
    return ""

def create_text_from_credential(credential_item: Dict[str, Any]) -> str:
    """
    Convert a credential item JSON into a human-readable text chunk.
    
    Args:
        credential_item: Dictionary with credential information
        
    Returns:
        Formatted credential text string
    """
    if not credential_item or "credential" not in credential_item:
        return ""
    
    if isinstance(credential_item["credential"], list) and credential_item["credential"]:
        return credential_item["credential"][0]
    elif isinstance(credential_item["credential"], str):
        return credential_item["credential"]
    
    return ""

def create_text_from_background(background_item: Dict[str, Any]) -> str:
    """
    Convert a background item JSON into a human-readable text chunk.
    
    Args:
        background_item: Dictionary with professional background information
        
    Returns:
        Formatted background text string
    """
    if not background_item:
        return ""
    
    background_text = extract_background_text(background_item)
    if not background_text:
        return ""
    
    # Add years of experience if available
    years = extract_background_years(background_item)
    industry = extract_background_industry(background_item)
    
    result = background_text
    
    if years and years > 0:
        year_word = "years" if years != 1 else "year"
        result += f" with at least {years} {year_word} of experience"
    
    if industry:
        result += f" in {industry}"
    
    return result

def extract_background_text(background_item: Dict[str, Any]) -> str:
    """Extract the background text from a background dictionary."""
    if not background_item or "background" not in background_item:
        return ""
    
    if isinstance(background_item["background"], list) and background_item["background"]:
        return background_item["background"][0]
    elif isinstance(background_item["background"], str):
        return background_item["background"]
    
    return ""

def extract_background_years(background_item: Dict[str, Any]) -> Union[int, float]:
    """Extract the years from a background dictionary."""
    if not background_item or "minyears" not in background_item:
        return 0
    
    if isinstance(background_item["minyears"], list) and background_item["minyears"]:
        try:
            return int(background_item["minyears"][0])
        except (ValueError, TypeError):
            return 0
    elif isinstance(background_item["minyears"], (int, float)):
        return background_item["minyears"]
    
    return 0

def extract_background_industry(background_item: Dict[str, Any]) -> str:
    """Extract the industry from a background dictionary."""
    if not background_item or "industry" not in background_item:
        return ""
    
    if isinstance(background_item["industry"], list) and background_item["industry"]:
        return ", ".join(background_item["industry"])
    elif isinstance(background_item["industry"], str):
        return background_item["industry"]
    
    return ""

# example usage:
if __name__ == "__main__":
    # Sample job data for testing
    sample_job = {
        "job_id": "job_123",
        "details": {
            "job_title": ["Software Engineer"],
            "employment_type": ["Full-time"],
            "experience_level": ["Mid-level"]
        },
        "mandatory": {
            "hard_skills": [
                {"skill": ["Python programming"], "minyears": [3]},
                {"skill": ["Web development"], "minyears": [2]}
            ],
            "education": [
                {"education_level": ["Bachelor's"], "field_of_study": ["Computer Science", "Software Engineering"]}
            ]
        },
        "preferred": {
            "hard_skills": [
                {"skill": ["Cloud services (AWS/Azure)"], "minyears": [1]}
            ]
        }
    }
    
    # generate chunks
    chunks = chunk_job_description(sample_job)
    
    # print chunks for testing
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Text: {chunk['text']}")
        print(f"Metadata: {chunk['metadata']}")