# Load Embedding Model for matching algorithm
# Needed to cache the JSON extract from the candidate resume

from sentence_transformers import SentenceTransformer
import torch
import streamlit as st

def load_sentence_model(
    model_name="intfloat/multilingual-e5-large-instruct",
    hf_token=st.secrets.model.token
    ):
    """
    Load the sentence model and moves it to the appropriate device (GPU if available)

    Args:
        model_name (str, optional): _description_. Defaults to "intfloat/multilingual-e5-large-instruct"

    Returns:
        model (SentenceTransformer): Sentence Transformer model

    Usage:
        model = load_setence_model()
    """
    model = SentenceTransformer(
        model_name,
        use_auth_token=hf_token,
        trust_remote_code=True
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model



