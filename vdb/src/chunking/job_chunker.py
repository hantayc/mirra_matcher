"""
job_chunker.py - chunking job description JSON into text chunks for embedding

Provides functions to convert structured job description JSON data into
human-readable text chunks for semantic vector embeddings, while preserving
context relationships between related items
"""

from typing import Dict, List, Any, Union, Optional
import re
import uuid

def chunk_job_description(job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a job description into chunks for embedding, preserving context relationships.
    
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
        chunks.extend(process_details(job_data["details"], job_id))
    
    # process mandatory qualifications
    if "mandatory" in job_data:
        chunks.extend(process_qualification_section(job_data["mandatory"], job_id, "mandatory"))
    
    # process preferred qualifications
    if "preferred" in job_data:
        chunks.extend(process_qualification_section(job_data["preferred"], job_id, "preferred"))
    
    # process responsibilities
    if "responsibility" in job_data:
        chunks.extend(process_responsibility_section(job_data["responsibility"], job_id))
    
    return chunks

def process_details(details: Dict[str, Any], job_id: str) -> List[Dict[str, Any]]:
    """Process the details section of a job description."""
    chunks = []
    
    # Extract job title as a chunk
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
        
    # extract location information if available
    if "location" in details and details["location"]:
        location = details["location"][0] if isinstance(details["location"], list) else details["location"]
        if isinstance(location, dict):
            location_parts = []
            if location.get("city"):
                location_parts.append(location["city"])
            if location.get("state"):
                location_parts.append(location["state"])
            if location.get("country"):
                location_parts.append(location["country"])
            
            if location_parts:
                location_text = ", ".join(location_parts)
                chunks.append({
                    "text": f"Location: {location_text}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "location",
                        "job_id": job_id
                    }
                })
    
    # extract work authorization requirements
    if "work_authorization" in details and details["work_authorization"]:
        auth = details["work_authorization"][0] if isinstance(details["work_authorization"], list) else details["work_authorization"]
        chunks.append({
            "text": f"Work authorization: {auth}",
            "metadata": {
                "source_type": "job_description",
                "chunk_type": "work_authorization",
                "job_id": job_id
            }
        })
    
    return chunks

def process_qualification_section(
    section: Dict[str, Any], 
    job_id: str, 
    requirement_level: str
) -> List[Dict[str, Any]]:
    """Process a qualification section (mandatory or preferred)."""
    chunks = []
    
    # Create a readable level for text
    readable_level = "Required" if requirement_level == "mandatory" else "Preferred"
    
    # Process hard skills
    if "hard_skills" in section:
        # Check if there's only one skill or multiple skills
        if len(section["hard_skills"]) == 1:
            skill = section["hard_skills"][0]
            skill_text = create_text_from_skill(skill)
            if skill_text:
                skill_name = extract_skill_name(skill)
                minyears = extract_minyears(skill)
                
                chunks.append({
                    "text": f"{readable_level} skill: {skill_text}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "skill",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "skill_name": skill_name,
                        "minyears": minyears,
                        "context_id": "",  # Empty string
                        "relationship_type": ""  # Single item has no relationship
                    }
                })
        else:
            # For multiple skills, check if they might be related (preserve context)
            context_id = str(uuid.uuid4())
            
            # Determine relationship type based on the section
            # In a mandatory section, skills are typically ALL required (AND relationship)
            # In a preferred section, skills might be alternatives (OR relationship)
            relationship_type = "AND" if requirement_level == "mandatory" else "OR"
            
            # First, process each skill individually
            for idx, skill in enumerate(section["hard_skills"]):
                skill_text = create_text_from_skill(skill)
                if skill_text:
                    skill_name = extract_skill_name(skill)
                    minyears = extract_minyears(skill)
                    
                    chunks.append({
                        "text": f"{readable_level} skill: {skill_text}",
                        "metadata": {
                            "source_type": "job_description",
                            "chunk_type": "skill",
                            "requirement_level": requirement_level,
                            "job_id": job_id,
                            "skill_name": skill_name,
                            "minyears": minyears,
                            "context_id": context_id,  # Shared context ID for related skills
                            "context_index": idx,      # Position in the related group
                            "context_total": len(section["hard_skills"]),  # Total items in group
                            "relationship_type": relationship_type  # How this relates to other items
                        }
                    })
            
            # Then, create a combined chunk that captures the relationship
            skill_names = [extract_skill_name(skill) for skill in section["hard_skills"] if extract_skill_name(skill)]
            if len(skill_names) > 1:
                # For large lists, use a more structured format
                if len(skill_names) > 5:
                    # Semi-colon separated for better readability with large lists
                    combined_skills = "; ".join(skill_names)
                    relation_desc = "all of these" if relationship_type == "AND" else "any of these"
                    text = f"{readable_level} skills (needs {relation_desc}): {combined_skills}"
                else:
                    # For smaller lists, use the more natural "X, Y, and Z" format
                    combined_skills = ", ".join(skill_names[:-1]) + " and " + skill_names[-1]
                    relation_phrase = "" if relationship_type == "AND" else "(any of these)"
                    text = f"{readable_level} skills {relation_phrase}: {combined_skills}"
                
                chunks.append({
                    "text": text,
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "skill_group",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "context_id": context_id,
                        "skill_count": len(skill_names),
                        "relationship_type": relationship_type
                    }
                })
    
    # Process education
    if "education" in section:
        context_id = str(uuid.uuid4()) if len(section["education"]) > 1 else ""
        relationship_type = "OR" if len(section["education"]) > 1 else ""
        
        # Process each education requirement individually
        for idx, edu in enumerate(section["education"]):
            edu_text = create_text_from_education(edu)
            if edu_text:
                chunks.append({
                    "text": f"{readable_level} education: {edu_text}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "education",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "context_id": context_id,
                        "context_index": idx if context_id else "",
                        "context_total": len(section["education"]) if context_id else "",
                        "relationship_type": relationship_type
                    }
                })
        
        # If multiple options, create a combined representation
        if len(section["education"]) > 1:
            edu_texts = [create_text_from_education(edu) for edu in section["education"] if create_text_from_education(edu)]
            if edu_texts:
                combined_edu = " OR ".join(edu_texts)
                chunks.append({
                    "text": f"{readable_level} education (alternatives): {combined_edu}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "education_group",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "context_id": context_id,
                        "relationship_type": relationship_type
                    }
                })
    
    # Process credentials
    if "credentials" in section:
        context_id = str(uuid.uuid4()) if len(section["credentials"]) > 1 else ""
        # Determine if credentials are all required or alternatives
        relationship_type = "AND" if requirement_level == "mandatory" else "OR"
        
        for idx, cred in enumerate(section["credentials"]):
            cred_text = create_text_from_credential(cred)
            if cred_text:
                chunks.append({
                    "text": f"{readable_level} credential: {cred_text}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "credential",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "context_id": context_id,
                        "context_index": idx if context_id else 0,
                        "context_total": len(section["credentials"]) if context_id else "",
                        "relationship_type": relationship_type if context_id else ""
                    }
                })
        
        # If multiple credentials, create a combined chunk
        if len(section["credentials"]) > 1:
            cred_texts = [create_text_from_credential(cred) for cred in section["credentials"] if create_text_from_credential(cred)]
            if cred_texts:
                if relationship_type == "AND":
                    combined_text = f"{readable_level} credentials (need all): "
                else:
                    combined_text = f"{readable_level} credentials (need any): "
                
                combined_creds = "; ".join(cred_texts) if len(cred_texts) > 3 else ", ".join(cred_texts)
                chunks.append({
                    "text": combined_text + combined_creds,
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "credential_group",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "context_id": context_id,
                        "relationship_type": relationship_type
                    }
                })
    
    # Process professional background
    if "professional_background" in section:
        # Check if there's a context relationship in backgrounds
        context_id = str(uuid.uuid4()) if len(section["professional_background"]) > 1 else ""
        
        # Professional backgrounds in job listings typically represent alternatives
        # (e.g., "X years in field A OR Y years in field B")
        relationship_type = "OR" if context_id else ""
        
        for idx, bg in enumerate(section["professional_background"]):
            bg_text = create_text_from_background(bg)
            if bg_text:
                minyears = extract_background_years(bg)
                industry = extract_background_industry(bg)
                
                # Enrich the experience text for better context
                enriched_text = enrich_experience_text(bg_text, minyears, industry, requirement_level)
                
                chunks.append({
                    "text": f"{readable_level} experience: {enriched_text}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "experience",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "minyears": minyears,
                        "industry": industry if industry else "",
                        "context_id": context_id,
                        "context_index": idx if context_id else 0,
                        "context_total": len(section["education"]) if context_id else 0,
                        "relationship_type": relationship_type
                    }
                })
        
        # Create a combined representation if multiple backgrounds
        if len(section["professional_background"]) > 1:
            bg_texts = [create_text_from_background(bg) for bg in section["professional_background"] 
                       if create_text_from_background(bg)]
            if bg_texts:
                # For professional experience, we usually want to explicitly show these are alternatives
                bg_combined = " OR ".join(bg_texts)
                chunks.append({
                    "text": f"{readable_level} experience (looking for one of the following): {bg_combined}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "experience_group",
                        "requirement_level": requirement_level,
                        "job_id": job_id,
                        "context_id": context_id,
                        "relationship_type": "OR"
                    }
                })
    
    return chunks


def enrich_experience_text(base_text: str, years: int, industry: str, requirement_level: str) -> str:
    """
    Enhance the experience description with additional context and details.
    
    Args:
        base_text: The basic experience text
        years: Years of experience required
        industry: Industry specification if any
        requirement_level: Whether this is mandatory or preferred
    
    Returns:
        Enhanced, more detailed experience description
    """
    # Start with the base text
    enriched = base_text
    
    # Add level descriptors based on years of experience
    if years:
        if years >= 10:
            enriched = f"Senior-level {enriched}"
        elif years >= 7:
            enriched = f"Experienced {enriched}"
        elif years >= 4:
            enriched = f"Mid-level {enriched}"
        elif years >= 1:
            enriched = f"Entry to mid-level {enriched}"
    
    # Add specific industry context if available
    if industry:
        if "in" not in enriched.lower():
            enriched += f" in {industry}"
    
    # Add emphasis for mandatory high-experience roles
    if requirement_level == "mandatory" and years and years >= 5:
        enriched += " (significant depth of experience required)"
    
    # If it's a role title that sounds generic, add more context
    generic_titles = ["manager", "leader", "specialist", "analyst", "consultant"]
    if any(title in base_text.lower() for title in generic_titles) and not "with" in base_text:
        enriched += " with project delivery responsibilities"
    
    return enriched

def process_responsibility_section(
    section: Dict[str, Any], 
    job_id: str
) -> List[Dict[str, Any]]:
    """Process the responsibility section."""
    chunks = []
    
    # Process hard skills as responsibilities
    if "hard_skills" in section:
        context_id = str(uuid.uuid4()) if len(section["hard_skills"]) > 1 else ""
        
        # For responsibilities, the relationship is almost always AND
        # (all responsibilities are expected to be fulfilled)
        relationship_type = "AND" if len(section["hard_skills"]) > 1 else ""
        
        for idx, skill in enumerate(section["hard_skills"]):
            skill_text = extract_skill_name(skill)
            if skill_text:
                # Enhance the responsibility description
                enhanced_resp = enhance_responsibility_description(skill_text)
                
                chunks.append({
                    "text": f"Job responsibility: {enhanced_resp}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "responsibility",
                        "requirement_level": "responsibility",
                        "job_id": job_id,
                        "context_id": context_id,
                        "context_index": idx if context_id else "",
                        "context_total": len(section["hard_skills"]) if context_id else "",
                        "relationship_type": relationship_type,
                        "responsibility_category": categorize_responsibility(skill_text)
                    }
                })
        
        # Create a combined chunk for related responsibilities
        if len(section["hard_skills"]) > 1:
            responsibility_texts = [extract_skill_name(skill) for skill in section["hard_skills"] 
                                   if extract_skill_name(skill)]
            if responsibility_texts:
                # For large groups of responsibilities, organize by formatting
                if len(responsibility_texts) > 7:
                    # Break into bullet points for better readability
                    bullets = "\n• " + "\n• ".join(responsibility_texts)
                    text = f"Core job responsibilities:{bullets}"
                else:
                    text = f"Job responsibilities include: {'; '.join(responsibility_texts)}"
                
                chunks.append({
                    "text": text,
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "responsibility_group",
                        "requirement_level": "responsibility",
                        "job_id": job_id,
                        "context_id": context_id,
                        "relationship_type": "AND",  # All responsibilities apply
                        "responsibility_count": len(responsibility_texts)
                    }
                })
    
    # Process professional background as responsibilities
    if "professional_background" in section:
        context_id = str(uuid.uuid4()) if len(section["professional_background"]) > 1 else ""
        relationship_type = "AND" if len(section["professional_background"]) > 1 else ""
        
        for idx, bg in enumerate(section["professional_background"]):
            bg_text = extract_background_text(bg)
            if bg_text:
                # Enhance the responsibility description
                enhanced_resp = enhance_responsibility_description(bg_text)
                
                chunks.append({
                    "text": f"Job responsibility: {enhanced_resp}",
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "responsibility",
                        "requirement_level": "responsibility",
                        "job_id": job_id,
                        "context_id": context_id,
                        "context_index": idx if context_id else "",
                        "context_total": len(section["professional_background"]) if context_id else "",
                        "relationship_type": relationship_type,
                        "responsibility_category": categorize_responsibility(bg_text)
                    }
                })
        
        # Create a combined chunk for related responsibilities
        if len(section["professional_background"]) > 1:
            bg_texts = [extract_background_text(bg) for bg in section["professional_background"] 
                       if extract_background_text(bg)]
            if bg_texts:
                # Format appropriately based on number of responsibilities
                if len(bg_texts) > 5:
                    bullets = "\n• " + "\n• ".join(bg_texts)
                    text = f"Additional responsibilities include:{bullets}"
                else:
                    text = f"Additional responsibilities include: {'; '.join(bg_texts)}"
                
                chunks.append({
                    "text": text,
                    "metadata": {
                        "source_type": "job_description",
                        "chunk_type": "responsibility_group",
                        "requirement_level": "responsibility",
                        "job_id": job_id,
                        "context_id": context_id,
                        "relationship_type": "AND",
                        "responsibility_count": len(bg_texts)
                    }
                })
    
    return chunks


def enhance_responsibility_description(resp_text: str) -> str:
    """
    Enhance a responsibility description to provide more context and detail.
    
    Args:
        resp_text: The basic responsibility text
        
    Returns:
        Enhanced responsibility description
    """
    # Start with the original text
    enhanced = resp_text
    
    # Add active voice and clarity for certain responsibility types
    lower_text = resp_text.lower()
    
    # Fix capitalization if needed
    if not resp_text[0].isupper() and len(resp_text) > 3:
        enhanced = resp_text[0].upper() + resp_text[1:]
    
    # Check if the text already starts with a verb; if not, consider adding one
    common_verbs = ["manage", "develop", "create", "lead", "design", "implement", 
                   "coordinate", "analyze", "monitor", "ensure", "build", "maintain"]
                   
    starts_with_verb = any(lower_text.startswith(verb) for verb in common_verbs)
    
    if not starts_with_verb:
        # Infer appropriate verb based on content
        if any(word in lower_text for word in ["strategy", "plan", "roadmap", "vision"]):
            enhanced = f"Develop and execute {enhanced}"
        elif any(word in lower_text for word in ["team", "staff", "personnel", "people"]):
            enhanced = f"Lead and support {enhanced}"
        elif any(word in lower_text for word in ["report", "metric", "data", "analytics"]):
            enhanced = f"Generate and analyze {enhanced}"
        elif any(word in lower_text for word in ["tool", "platform", "system", "application"]):
            enhanced = f"Build and maintain {enhanced}"
    
    # Ensure the description ends with proper punctuation
    if not enhanced.endswith((".", "!", "?")):
        enhanced += "."
    
    return enhanced


def categorize_responsibility(resp_text: str) -> str:
    """
    Categorize a responsibility into a general category.
    
    Args:
        resp_text: The responsibility text
        
    Returns:
        Category string
    """
    lower_text = resp_text.lower()
    
    # Check for different categories
    if any(word in lower_text for word in ["develop", "build", "code", "program", "implement", "architecture", "design system"]):
        return "development"
    elif any(word in lower_text for word in ["lead", "manage", "direct", "supervise", "mentor", "guide"]):
        return "leadership"
    elif any(word in lower_text for word in ["analyze", "research", "study", "evaluate", "assess", "investigate"]):
        return "analysis"
    elif any(word in lower_text for word in ["collaborate", "team", "communicate", "coordinate", "partner"]):
        return "collaboration"
    elif any(word in lower_text for word in ["strategy", "plan", "roadmap", "vision", "direction"]):
        return "strategy"
    elif any(word in lower_text for word in ["customer", "client", "stakeholder", "user", "support"]):
        return "customer_interaction"
    elif any(word in lower_text for word in ["test", "qa", "quality", "review", "verify", "validate"]):
        return "quality_assurance"
    elif any(word in lower_text for word in ["document", "report", "present", "communicate"]):
        return "documentation"
    elif any(word in lower_text for word in ["maintain", "monitor", "operate", "support", "troubleshoot"]):
        return "operations"
    elif any(word in lower_text for word in ["innovate", "research", "explore", "discover", "proof of concept", "poc"]):
        return "innovation"
    else:
        return "general"

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
    field_of_study = []
    if "field_of_study" in education_item and education_item["field_of_study"]:
        if isinstance(education_item["field_of_study"], list):
            field_of_study = education_item["field_of_study"]
        elif isinstance(education_item["field_of_study"], str):
            field_of_study = [education_item["field_of_study"]]
    
    # Combine into a natural language statement
    if education_level and field_of_study:
        return f"{education_level} in {', '.join(field_of_study)}"
    elif education_level:
        return f"{education_level}"
    elif field_of_study:
        return f"Degree in {', '.join(field_of_study)}"
    
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
    
    # Check if background_text is a comma-separated list (indicating multiple skills)
    if "," in background_text:
        # This might be a list of related skills/technologies
        # Handle it as a single experience that requires multiple related skills
        skills_list = [skill.strip() for skill in background_text.split(",")]
        
        # Create a more natural list format for better readability
        if len(skills_list) > 5:
            # For longer lists, keep the comma separated format but add "and" before the last item
            formatted_list = ", ".join(skills_list[:-1]) + ", and " + skills_list[-1]
            background_text = f"Experience with multiple technologies including {formatted_list}"
        else:
            # For shorter lists, use a more flowing format
            if len(skills_list) == 2:
                formatted_list = " and ".join(skills_list)
            else:
                formatted_list = ", ".join(skills_list[:-1]) + ", and " + skills_list[-1]
            background_text = f"Experience with {formatted_list}"
    
    # Add years of experience if available
    years = extract_background_years(background_item)
    industry = extract_background_industry(background_item)
    
    result = background_text
    
    if years and years > 0:
        year_word = "years" if years != 1 else "year"
        # Use more descriptive language for different experience levels
        if years >= 10:
            result += f" with extensive ({years}+ {year_word}) professional experience"
        elif years >= 7:
            result += f" with significant ({years}+ {year_word}) professional experience"
        elif years >= 4:
            result += f" with substantial ({years}+ {year_word}) professional experience" 
        elif years >= 2:
            result += f" with proven ({years}+ {year_word}) professional experience"
        else:
            result += f" with at least {years} {year_word} of experience"
    
    if industry:
        # Make industry descriptions more specific and informative
        if "," in industry:
            industries = [ind.strip() for ind in industry.split(",")]
            if len(industries) == 2:
                formatted_industries = " or ".join(industries)
            else:
                formatted_industries = ", ".join(industries[:-1]) + ", or " + industries[-1]
            result += f" in industries such as {formatted_industries}"
        else:
            result += f" in the {industry} industry"
    
    return result

def extract_background_text(background_item: Dict[str, Any]) -> str:
    """Extract the background text from a background dictionary."""
    if not background_item or "background" not in background_item:
        return ""
    
    if isinstance(background_item["background"], list) and background_item["background"]:
        # Background might be a single string or a list of skills that should be grouped
        if len(background_item["background"]) == 1:
            return background_item["background"][0]
        else:
            # Join multiple backgrounds as a comma-separated list
            return ", ".join(background_item["background"])
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
            ],
            "professional_background": [
                {"background": ["OpenShift", "Google Cloud Platform", "DevOps"], "minyears": [2]}
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

