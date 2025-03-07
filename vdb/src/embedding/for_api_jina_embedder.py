""" import json
import boto3
import numpy as np
from typing import List, Union

class JinaEmbedder:
    def __init__(self, endpoint_name: str, region: str = "us-east-1"):
        """
        Initialize the Jina embedder with a SageMaker endpoint.
        
        Args:
            endpoint_name: Name of the SageMaker endpoint running jina-embeddings-v3
            region: AWS region where the endpoint is deployed
        """
        self.endpoint_name = endpoint_name
        self.region = region
        self.client = boto3.client('sagemaker-runtime', region_name=region)
        
    def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Generate embeddings using jina-embeddings-v3 through SageMaker endpoint.
        
        Args:
            texts: Single text or list of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]
            
        # Prepare the payload for the jina-embeddings-v3 model
        payload = {
            "input": texts,
        }
        
        # Call the SageMaker endpoint
        response = self.client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        # Parse the response
        result = json.loads(response['Body'].read().decode())
        embeddings = result['embeddings']
        
        # Convert to native Python floats if necessary
        if embeddings and any(isinstance(val, (np.number, np.floating)) for val in embeddings[0]):
            embeddings = [[float(val) for val in emb] for emb in embeddings]
        
        return embeddings
"""