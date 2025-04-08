import traceback
import torch
from sentence_transformers import util
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from init_pinecone import pinecone_index, sentence_model, embedding_cache

# Adjust this as needed
PINECONE_FETCH_TIMEOUT = 30  # seconds

# We assume the model is loaded on GPU. Optionally:
device = sentence_model.device  # Use the device that the model is on

def get_embedding(text: str):
    text = text.strip()
    
    # Check local cache
    if text in embedding_cache:
        return embedding_cache[text]

    # Attempt to fetch from Pinecone with a timeout
    fetch_result = None
    if pinecone_index is not None:
        def fetch_pinecone_vector():
            return pinecone_index.fetch(ids=[text])
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fetch_pinecone_vector)
            try:
                fetch_result = future.result(timeout=PINECONE_FETCH_TIMEOUT)
            except TimeoutError:
                # Timed out, we'll skip Pinecone
                fetch_result = None
            except Exception as e:
                # Some other Pinecone/network error
                print(f"Error while fetching from Pinecone: {e}")
                fetch_result = None

    # If Pinecone is unavailable, timed out, or returns empty,
    # compute locally on GPU.
    if not fetch_result or not fetch_result.vectors:
        emb_tensor = sentence_model.encode(text, convert_to_tensor=True)
        embedding_cache[text] = emb_tensor  # keep on GPU
        return embedding_cache[text]
    else:
        # Found in Pinecone -> convert to GPU tensor using the model's device.
        fetched_vector = fetch_result.vectors[text].values
        emb_tensor = torch.tensor(fetched_vector, device=device)
        embedding_cache[text] = emb_tensor
        return emb_tensor

def cosine_similarity(vec1, vec2):
    # Both vectors should be on GPU (or on the same device)
    return util.cos_sim(vec1, vec2)

def compute_semantic_similarity(text1: str, text2: str) -> float:
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    raw_similarity = float(util.cos_sim(emb1, emb2))
    normalized = (raw_similarity - 0.7) / 0.3
    return max(0.0, min(1.0, normalized))

def nlp_similarity_cached(text1: str, text2: str) -> float:
    return compute_semantic_similarity(text1, text2)