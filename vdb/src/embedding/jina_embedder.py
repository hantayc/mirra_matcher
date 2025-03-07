import json
import os
from typing import List, Union
import numpy as np

class JinaEmbedder:
    def __init__(self, api_key: str = None):
        """
        Initialize the Jina embedder using the direct API.
        
        Args:
            api_key: Jina API key (optional, can also use JINA_API_KEY env variable)
        """
        try:
            from jinaai.embeddings import Embeddings
        except ImportError:
            raise ImportError("jinaai package not found. Install with: pip install jinaai")
            
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.environ.get("JINA_API_KEY")
        if not self.api_key:
            print("Warning: No Jina API key provided. Set JINA_API_KEY environment variable.")
        
        # Initialize the Jina Embeddings client
        self.embedder = Embeddings(
            model="jina-embeddings-v3-base-en",
            api_key=self.api_key
        )
        
    def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings using jina-embeddings-v3 through direct API.
        
        Args:
            texts: Single text or list of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]
            
        # Call the Jina API
        results = self.embedder.embed_batch(texts)
        
        # Extract and convert embeddings to native Python floats
        embeddings = []
        for result in results:
            # Convert to native float to ensure compatibility
            embedding = [float(value) for value in result.embedding]
            embeddings.append(embedding)
            
        return embeddings