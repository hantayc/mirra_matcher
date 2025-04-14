from pinecone import Pinecone
from utils.embeddings import EmbeddingGenerator
import json

class PineconeDatabase:
    """Class for pinecone database to access and to retrieve"""
    def __init__(self, api_key, index_name, aws_region, sagemaker_endpoint, namespace="job_strings"):
        self.api_key = api_key
        self.index_name = index_name
        self.aws_region = aws_region
        self.namespace = namespace
        self.embedder = EmbeddingGenerator(endpoint_name=sagemaker_endpoint, region=aws_region, embedding_dimension=1024)
        
    def connect_to_pinecone(self):
        """
        Connect to existing Pinecone index
        Returns:
            Pinecone index object
        """
        try:
            # Initialize Pinecone client
            pc = Pinecone(api_key=self.api_key)
        
            # Connect to the existing index
            index = pc.Index(self.index_name)
            self.index = index
            
            return index
        
        except Exception as e:
            print(f"Error connecting to Pinecone: {str(e)}")
            return None
        
    def search(self, keyword, filters):
        query_embedding = self.embedder.generate_embeddings([keyword])[0]
        search_results = self.index.query(vector=query_embedding, filter=filters, top_k=200, include_metadata=False)

        return search_results['matches']
