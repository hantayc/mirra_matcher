from typing import Dict, List, Any
from ..embedding.jina_embedder import JinaEmbedder
from ..vector_db.pinecone_client import PineconeClient
from ..chunking.resume_chunker import chunk_resume

def find_matching_jobs(
    resume_data: Dict[str, Any],
    embedder: JinaEmbedder,
    pinecone_client: PineconeClient,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Find matching jobs for a resume.
    
    Args:
        resume_data: Resume data dictionary
        embedder: JinaEmbedder instance
        pinecone_client: PineconeClient instance
        top_k: Number of top matching jobs to return
        
    Returns:
        List of matching jobs with scores
    """
    # Generate chunks from resume
    resume_chunks = chunk_resume(resume_data)
    
    # Dictionary to store job scores
    job_scores = {}
    job_metadata = {}
    job_matches = {}
    
    # Process each resume chunk
    for chunk in resume_chunks:
        # Generate embedding
        chunk_text = chunk["text"]
        chunk_type = chunk["metadata"]["chunk_type"]
        
        # Use appropriate instruction based on chunk type
        if chunk_type == "skill":
            instruction = "Represent this skill qualification for job-resume matching"
        elif chunk_type == "education":
            instruction = "Represent this educational qualification for job-resume matching"
        elif chunk_type == "experience":
            instruction = "Represent this professional experience for job-resume matching"
        else:
            instruction = "Represent this qualification for job-resume matching"
        
        embedding = embedder.generate_embeddings(chunk_text, instruction)[0]
        
        # Search for matching job qualifications
        filter = {
            "source_type": "job_description",
            "chunk_type": chunk_type
        }
        
        results = pinecone_client.search(embedding, filter=filter, top_k=5)
        
        # Process search results
        for match in results["matches"]:
            job_id = match["metadata"]["job_id"]
            match_score = match["score"]
            
            # Initialize job data if not seen before
            if job_id not in job_scores:
                job_scores[job_id] = []
                job_matches[job_id] = []
                job_metadata[job_id] = {
                    "job_title": match["metadata"]["job_title"],
                    "company_name": match["metadata"]["company_name"],
                    "requirements": []
                }
            
            # Add score
            job_scores[job_id].append(match_score)
            
            # Store match details
            job_matches[job_id].append({
                "resume_qualification": chunk_text,
                "job_requirement": match["metadata"]["chunk_text"],
                "match_score": match_score,
                "resume_metadata": chunk["metadata"],
                "job_metadata": match["metadata"]
            })
            
            # Add requirement if not already present
            req = match["metadata"]["chunk_text"]
            if req not in job_metadata[job_id]["requirements"]:
                job_metadata[job_id]["requirements"].append(req)
    
    # Calculate overall score for each job
    results = []
    for job_id, scores in job_scores.items():
        # Calculate overall score (average of top scores)
        top_scores = sorted(scores, reverse=True)[:min(5, len(scores))]
        avg_score = sum(top_scores) / len(top_scores)
        
        # Create result entry
        result = {
            "job_id": job_id,
            "match_score": avg_score,
            "metadata": job_metadata[job_id],
            "matching_qualifications": sorted(job_matches[job_id], key=lambda x: x["match_score"], reverse=True)
        }
        
        results.append(result)
    
    # Sort by match score and take top_k
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)[:top_k]
    
    return results

def calculate_qualification_gaps(
    resume_data: Dict[str, Any],
    job_data: Dict[str, Any],
    embedder: JinaEmbedder
) -> List[Dict[str, Any]]:
    """
    Calculate qualification gaps between resume and job.
    
    Args:
        resume_data: Resume data dictionary
        job_data: Job data dictionary
        embedder: JinaEmbedder instance
        
    Returns:
        List of qualification gaps
    """
    # Implementation for qualification gap analysis
    # This would analyze which mandatory job requirements aren't matched well in the resume
    
    # Example implementation outline:
    # 1. Chunk both resume and job
    # 2. Generate embeddings for all chunks
    # 3. For each mandatory job requirement, find best matching resume qualification
    # 4. If match score is below threshold, consider it a gap
    
    # Placeholder - implementation
    return []