# Load Embedding Model for matching algorithm
# Needed to cache the JSON extract from the candidate resume

from sentence_transformers import SentenceTransformer
import torch
import streamlit as st

@st.cache_resource
def load_sentence_model(
    model_name="intfloat/multilingual-e5-large-instruct",
    hf_token=st.secrets.model.token
):
    """
    Load the SentenceTransformer model onto GPU if available, else CPU.
    """
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(
        model_name,
        token=hf_token,
        trust_remote_code=True,
        device=device_str
    )
    return model

