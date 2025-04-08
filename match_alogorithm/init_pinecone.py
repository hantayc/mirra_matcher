import os
import traceback
import streamlit as st
import torch

from sentence_transformers import util
from pinecone import Pinecone

from utils.load_embedding_fn import load_sentence_model

try:
    # Instantiate Pinecone client and get the index
    pc = Pinecone(api_key=st.secrets.pinecone.api_key, environment=st.secrets.pinecone.aws_regionT)
    pinecone_index = pc.Index(st.secrets.pinecone.index_name)
    print("Pinecone connected successfully!")
except Exception as e:
    # If any error occurs, print it and fallback to None
    print("Error connecting to Pinecone, proceeding without it:", str(e))
    pc = None
    pinecone_index = None

# Always load the SentenceTransformer model
sentence_model = load_sentence_model()

# Create local caches for embeddings and similarities
embedding_cache = {}
similarity_cache = {}