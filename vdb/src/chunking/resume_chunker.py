"""
resume_chunker.py - Module for chunking resume JSON into text chunks for embedding.

Functions to convert structured resume JSON data into
human-readable text chunks suitable for semantic vector embedding.
"""

from typing import Dict, List, Any, Union
import re
import uuid

def chunk_resume(resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a resume into chunks for embedding.
    
    Args:
        resume_data: Resume dictionary with qualification data
        
    Returns:
        List of chunks, each with text and metadata
    """
    chunks = []
    
    # validate input
    if not isinstance(resume_data, dict):
        raise ValueError("Resume data must be a dictionary")
    
    # extract resume ID (or generate one if not present)
    resume_id = resume_data.get("resume_id")
    if not resume_id:
        resume_id = str(uuid.uuid4())
        resume_data["resume_id"] = resume_id
    
    # process skills
    if "skills" in resume_data and resume_data["skills"]:
        for idx, skill in enumerate(resume_data["skills"]):
            skill_text = create_text_from_skill(skill)
            if skill_text:
                skill_name = extract_skill_name(skill)
                years = extract_skill_years(skill)
                
                chunks.append({
                    "text": skill_text,
                    "metadata": {
                        "source_type": "resume",
                        "chunk_type": "skill",
                        "resume_id": resume_id,
                        "skill_name": skill_name,
                        "years": years
                    }
                })
    
    # process education
    if "education" in resume_data and resume_data["education"]:
        for idx, edu in enumerate(resume_data["education"]):
            edu_text = create_text_from_education(edu)
            if edu_text:
                education_level = extract_education_level(edu)
                major = extract_education_major(edu)
                minor = extract_education_minor(edu)
                
                chunks.append({
                    "text": edu_text,
                    "metadata": {
                        "source_type": "resume",
                        "chunk_type": "education",
                        "resume_id": resume_id,
                        "education_level": education_level,
                        "major": major,
                        "minor": minor
                    }
                })
    
    # process professional background
    if "professional_background" in resume_data and resume_data["professional_background"]:
        for idx, bg in enumerate(resume_data["professional_background"]):
            bg_text = create_text_from_background(bg)
            if bg_text:
                background = extract_background_text(bg)
                years = extract_background_years(bg)
                industry = extract_background_industry(bg)
                
                chunks.append({
                    "text": bg_text,
                    "metadata": {
                        "source_type": "resume",
                        "chunk_type": "experience",
                        "resume_id": resume_id,
                        "background": background,
                        "years": years,
                        "industry": industry
                    }
                })
    
    # process credentials
    if "credentials" in resume_data and resume_data["credentials"]:
        for idx, cred in enumerate(resume_data["credentials"]):
            cred_text = create_text_from_credential(cred)
            if cred_text:
                credential = extract_credential(cred)
                
                chunks.append({
                    "text": f"Credential: {cred_text}",
                    "metadata": {
                        "source_type": "resume",
                        "chunk_type": "credential",
                        "resume_id": resume_id,
                        "credential": credential
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
    years = extract_skill_years(skill_item)
    if years and years > 0:
        year_word = "years" if years != 1 else "year"
        return f"Skill: {skill_text} with {years} {year_word} of experience"
    
    return f"Skill: {skill_text}"

def extract_skill_name(skill_item: Dict[str, Any]) -> str:
    """Extract the skill name from a skill dictionary."""
    if not skill_item or "skill" not in skill_item:
        return ""
    
    if isinstance(skill_item["skill"], list) and skill_item["skill"]:
        return skill_item["skill"][0]
    elif isinstance(skill_item["skill"], str):
        return skill_item["skill"]
    
    return ""

def extract_skill_years(skill_item: Dict[str, Any]) -> Union[int, float]:
    """Extract the years from a skill dictionary."""
    if not skill_item or "years" not in skill_item:
        return 0
    
    if isinstance(skill_item["years"], (int, float)):
        return skill_item["years"]
    elif isinstance(skill_item["years"], list) and skill_item["years"]:
        try:
            return float(skill_item["years"][0])
        except (ValueError, TypeError):
            return 0
    
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
    education_level = extract_education_level(education_item)
    
    # Extract major fields
    major = extract_education_major(education_item)
    
    # Extract minor fields
    minor = extract_education_minor(education_item)
    
    # Combine into a natural language statement
    result = "Education: "
    
    if education_level and major:
        result += f"{education_level} in {major}"
    elif education_level:
        result += f"{education_level} degree"
    elif major:
        result += f"Degree in {major}"
    else:
        return ""  # No education details to report
    
    if minor:
        result += f" with minor in {minor}"
    
    return result

def extract_education_level(education_item: Dict[str, Any]) -> str:
    """Extract the education level from an education dictionary."""
    if not education_item or "education_level" not in education_item:
        return ""
    
    if isinstance(education_item["education_level"], str):
        return education_item["education_level"]
    elif isinstance(education_item["education_level"], list) and education_item["education_level"]:
        return education_item["education_level"][0]
    
    return ""

def extract_education_major(education_item: Dict[str, Any]) -> str:
    """Extract the major field(s) from an education dictionary."""
    if not education_item or "major" not in education_item:
        return ""
    
    if isinstance(education_item["major"], list) and education_item["major"]:
        return ", ".join(education_item["major"])
    elif isinstance(education_item["major"], str):
        return education_item["major"]
    
    # Check for field_of_study as alternative (job JSON format)
    if "field_of_study" in education_item:
        if isinstance(education_item["field_of_study"], list) and education_item["field_of_study"]:
            return ", ".join(education_item["field_of_study"])
        elif isinstance(education_item["field_of_study"], str):
            return education_item["field_of_study"]
    
    return ""

def extract_education_minor(education_item: Dict[str, Any]) -> str:
    """Extract the minor field(s) from an education dictionary."""
    if not education_item or "minor" not in education_item:
        return ""
    
    if isinstance(education_item["minor"], list) and education_item["minor"]:
        return ", ".join(education_item["minor"])
    elif isinstance(education_item["minor"], str):
        return education_item["minor"]
    
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
    
    result = f"Experience: {background_text}"
    
    if years and years > 0:
        year_word = "years" if years != 1 else "year"
        result += f" with {years} {year_word} of experience"
    
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
    if not background_item or "years" not in background_item:
        return 0
    
    if isinstance(background_item["years"], (int, float)):
        return background_item["years"]
    elif isinstance(background_item["years"], list) and background_item["years"]:
        try:
            return float(background_item["years"][0])
        except (ValueError, TypeError):
            return 0
    
    # Check for minyears as alternative (job JSON format)
    if "minyears" in background_item:
        if isinstance(background_item["minyears"], (int, float)):
            return background_item["minyears"]
        elif isinstance(background_item["minyears"], list) and background_item["minyears"]:
            try:
                return float(background_item["minyears"][0])
            except (ValueError, TypeError):
                return 0
    
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

def create_text_from_credential(credential_item: Dict[str, Any]) -> str:
    """
    Convert a credential item JSON into a human-readable text chunk.
    
    Args:
        credential_item: Dictionary with credential information
        
    Returns:
        Formatted credential text string
    """
    if not credential_item:
        return ""
    
    credential = extract_credential(credential_item)
    if not credential:
        return ""
    
    return credential

def extract_credential(credential_item: Dict[str, Any]) -> str:
    """Extract the credential from a credential dictionary."""
    if not credential_item or "credential" not in credential_item:
        return ""
    
    if isinstance(credential_item["credential"], list) and credential_item["credential"]:
        return credential_item["credential"][0]
    elif isinstance(credential_item["credential"], str):
        return credential_item["credential"]
    
    return ""

# example usage:
if __name__ == "__main__":
    # Sample resume data for testing
    sample_resume = {
        "resume_id": "resume_456",
        "skills": [
            {"skill": ["Python programming"], "years": 3.5},
            {"skill": ["Data analysis"], "years": 2}
        ],
        "education": [
            {
                "education_level": "Master's",
                "major": ["Computer Science"],
                "minor": ["Statistics"]
            },
            {
                "education_level": "Bachelor's",
                "major": ["Electrical Engineering"],
                "minor": []
            }
        ],
        "professional_background": [
            {
                "background": ["Data Scientist"],
                "years": 2.5,
                "industry": ["Technology"]
            },
            {
                "background": ["Research Assistant"],
                "years": 1.5,
                "industry": ["Academia"]
            }
        ],
        "credentials": [
            {"credential": ["AWS Certified Developer"]},
            {"credential": ["Machine Learning Certification"]}
        ]
    }
    
    # generate chunks
    chunks = chunk_resume(sample_resume)
    
    # Print chunks for testing
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Text: {chunk['text']}")
        print(f"Metadata: {chunk['metadata']}")