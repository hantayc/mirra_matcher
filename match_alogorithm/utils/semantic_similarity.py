import torch
from sentence_transformers import util
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from match_alogorithm.init_pinecone import pinecone_index, embedding_cache

from utils.embeddings import EmbeddingGenerator

embedder = EmbeddingGenerator(
    endpoint_name="e5-embeddings-huggingface",
    region="us-east-1",           # e.g. "us-east-1"
    embedding_dimension=1024            # match your model dimension
)

# GPU If Avail
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

PINECONE_FETCH_TIMEOUT = 30  # seconds

def get_embedding(text: str):
    """
    Return the embedding of 'text' from:
    1) local cache (if available),
    2) Pinecone (if fetchable by ID),
    3) otherwise, call your SageMaker endpoint via EmbeddingGenerator.
    """
    text = text.strip()

    # Check local cache first
    if text in embedding_cache:
        return embedding_cache[text]

    fetch_result = None
    # Attempt to fetch from Pinecone with a timeout
    if pinecone_index is not None:
        def fetch_pinecone_vector():
            return pinecone_index.fetch(ids=[text])
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fetch_pinecone_vector)
            try:
                fetch_result = future.result(timeout=PINECONE_FETCH_TIMEOUT)
            except TimeoutError:
                fetch_result = None
            except Exception as e:
                print(f"Error while fetching from Pinecone: {e}")
                fetch_result = None

    if not fetch_result or not fetch_result.vectors:
        emb_list = embedder.generate_embeddings([text])  # returns list of lists
        if emb_list and len(emb_list) > 0:
            emb_tensor = torch.tensor(emb_list[0], device=device)
        else:
            emb_tensor = torch.zeros(embedder.embedding_dimension, device=device)
        
        embedding_cache[text] = emb_tensor
        return emb_tensor
    else:
        fetched_vector = fetch_result.vectors[text].values
        emb_tensor = torch.tensor(fetched_vector, device=device)
        embedding_cache[text] = emb_tensor
        return emb_tensor

# No Pinecone Leverage
# def get_embedding(text: str):
#     """
#     Return the embedding for 'text' using:
#     1) a local cache (if available),
#     2) otherwise, call your SageMaker endpoint via embedder.generate_embeddings.
    
#     This version does not attempt to fetch embeddings from Pinecone.
#     """
#     text = text.strip()

#     # Check local cache first.
#     if text in embedding_cache:
#         return embedding_cache[text]

#     # Call your SageMaker endpoint or generate embeddings via embedder.
#     emb_list = embedder.generate_embeddings([text])  # returns a list of lists
#     if emb_list and len(emb_list) > 0:
#         emb_tensor = torch.tensor(emb_list[0], device=device)
#     else:
#         emb_tensor = torch.zeros(embedder.embedding_dimension, device=device)
    
#     embedding_cache[text] = emb_tensor
#     return emb_tensor

def cosine_similarity(vec1, vec2):
    return util.cos_sim(vec1, vec2)

def compute_semantic_similarity(text1: str, text2: str) -> float:
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    raw_similarity = float(util.cos_sim(emb1, emb2))

    # The same normalization you had before (optional)
    normalized = (raw_similarity - 0.7) / 0.3
    return max(0.0, min(1.0, normalized))

def nlp_similarity_cached(text1: str, text2: str) -> float:
    return compute_semantic_similarity(text1, text2)