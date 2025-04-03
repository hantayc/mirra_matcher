import os
import traceback
import torch

from sentence_transformers import util
from pinecone import Pinecone

from utils.load_embedding_fn import load_sentence_model

PINECONE_API_KEY = (
    "pcsk_7VkStS_ifR3SH9d1MSkkju9kP7DUt5M16CpNyzi9dwNBm7iUqyXmbKZWQbC55ZzfSEaAB"
)
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = "sample-100-strings"  # Must match an existing index or be created

# Instantiate Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

# Now get a handle to your Pinecone index
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

# Load your SentenceTransformer model
sentence_model = load_sentence_model()

# Local cache to prevent repeated fetches in the same session
embedding_cache = {}
