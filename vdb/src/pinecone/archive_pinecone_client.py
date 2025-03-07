import pinecone
from typing import Dict, List, Any
from ..embedding.jina_embedder import JinaEmbedder

class PineconeClient:
    def __init__(
        self, 
        api_key: str, 
        environment: str,
        index_name: str = "mirra",
        dimension: int = 1024,  
        embedder: JinaEmbedder = None
    ):
        """Initialize the Pinecone client with configuration."""
        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                metadata_config={"indexed": ["type", "source", "requirement_type"]}
            )
     
        # Connect to index
        self.index = pinecone.Index(index_name)
        self.embedder = embedder
    
    def index_documents(self, doc_id: str, chunks: List[Dict[str, Any]]) -> int:
        """Index document chunks into Pinecone."""
        vectors = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding using Jina
            embedding = self.embedder.generate_embeddings(chunk["text"])[0]  # Get first (only) embedding
            
            # Create vector ID
            vector_id = f"{doc_id}_chunk_{i}"
            
            # Prepare vector
            vector = {
                "id": vector_id,
                "values": embedding,
                "metadata": {
                    "doc_id": doc_id,
                    "chunk_text": chunk["text"],
                    **chunk["metadata"]
                }
            }
            
            vectors.append(vector)
        
        # Upload vectors in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            self.index.upsert(vectors=batch)
        
        return len(vectors)