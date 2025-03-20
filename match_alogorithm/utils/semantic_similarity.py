from sentence_transformers import util  # Import the util module for cosine similarity
from .load_embedding_fn import load_sentence_model


sentence_model = load_sentence_model()

embedding_cache = {}


def get_embedding(text: str):
    text = text.strip()
    if text in embedding_cache:
        return embedding_cache[text]
    else:
        emb = sentence_model.encode(text, convert_to_tensor=True)
        embedding_cache[text] = emb
        return emb


def cosine_similarity(vec1, vec2):
    return util.cos_sim(vec1, vec2)


def compute_semantic_similarity(text1: str, text2: str) -> float:
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    raw_similarity = float(util.cos_sim(emb1, emb2))
    normalized = (raw_similarity - 0.7) / 0.3
    normalized = max(0.0, min(1.0, normalized))
    return normalized


def nlp_similarity_cached(text1: str, text2: str) -> float:
    return compute_semantic_similarity(text1, text2)
