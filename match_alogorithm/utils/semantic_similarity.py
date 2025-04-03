from sentence_transformers import util  # Import the util module for cosine similarity
from .load_embedding_fn import load_sentence_model
import traceback

sentence_model = load_sentence_model()

embedding_cache = {}


def get_embedding(text):
    try:
        # If text is a list, join it into a single string
        if isinstance(text, list):
            print("Warning: text is a list. Joining elements...")
            text = " ".join([str(t) for t in text])

        text = text.strip()

    except Exception as e:
        print("Error during strip():", text, "of type", type(text))
        traceback.print_exc()
        raise e

    if text in embedding_cache:
        return embedding_cache[text]
    else:
        try:
            emb = sentence_model.encode(text, convert_to_tensor=True)
        except Exception as e:
            print("Error during encoding text:", text)
            traceback.print_exc()
            raise e
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
