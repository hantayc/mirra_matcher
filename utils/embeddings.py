import boto3
import json
import numpy as np

class EmbeddingGenerator:
    """Class for embedding generation using SageMaker endpoint"""
    
    def __init__(self, endpoint_name, region, embedding_dimension=1024):
        """
        Initialize with SageMaker endpoint
        Args:
            endpoint_name: Name of the SageMaker endpoint
            region: AWS region
            embedding_dimension: Dimension of the embedding vectors
        """
        self.endpoint_name = endpoint_name
        self.region = region
        self.embedding_dimension = embedding_dimension
        
        # Initialize SageMaker runtime client
        self.client = boto3.client(
            "sagemaker-runtime",
            region_name="us-east-1",
            aws_access_key_id=st.secrets["aws"]["access_key_id"],
            aws_secret_access_key=st.secrets["aws"]["secret_access_key"]
        )
        print(f"Initialized SageMaker embedder for endpoint: {endpoint_name}")

    def encode(self, texts, batch_size=100, convert_to_tensor=False):
        """
        Compatibility method to match the interface expected by precompute_embeddings_for_df
        
        Args:
            texts: List of texts to embed
            batch_size: Size of each batch (ignored, using internal batching)
            convert_to_tensor: Whether to convert to tensor (ignored)
            
        Returns:
            List of embedding vectors
        """
        return self.generate_embeddings(texts)
    
    def generate_embeddings(self, texts, instructions=None):
        """
        Generate embeddings using SageMaker endpoint
        Args:
            texts: String or list of texts to embed
            instructions: Optional instructions for the model
        Returns:
            List of embedding vectors
        """
        # Ensure texts is a list
        if not isinstance(texts, list):
            texts = [texts]
        
        return self._generate_with_sagemaker(texts, instructions)
    
    def _generate_with_sagemaker(self, texts, instructions=None):
        """Generate embeddings using SageMaker endpoint"""
        try:
            embeddings = []
            
            for text in texts:
                # For E5 models, a common format is:
                payload = {
                    "inputs": [text]  # Send as a list of strings
                }
                
                if instructions:
                    # Some E5 models may expect a specific instruction format
                    formatted_text = f"{instructions}: {text}"
                    payload = {
                        "inputs": [formatted_text]
                    }
                
                # Invoke the SageMaker endpoint
                response = self.client.invoke_endpoint(
                    EndpointName=self.endpoint_name,
                    ContentType="application/json",
                    Body=json.dumps(payload)
                )
                
                # Parse the response
                response_body = json.loads(response["Body"].read())
                
                # Debugging output to inspect response structure
                # print(f"Response type: {type(response_body)}")
                # if isinstance(response_body, list):
                #     print(f"Response length: {len(response_body)}")
                #     if len(response_body) > 0:
                #         print(f"First element type: {type(response_body[0])}")
                #         print(f"First element length: {len(response_body[0])}")
                
                # Extract embedding
                embedding = None
                if isinstance(response_body, list) and len(response_body) > 0:
                    if isinstance(response_body[0], list) and len(response_body[0]) > 0:
                        if isinstance(response_body[0][0], list):
                            # It's a 3D array, extract the innermost array
                            embedding = response_body[0][0]
                        else:
                            # It's a 2D array
                            embedding = response_body[0]
                    else:
                        # It's a 1D array or other structure
                        embedding = response_body
                else:
                    # It's not a list
                    embedding = response_body
                
                # If the embedding is a nested list that wasn't properly flattened, flatten one level.
                if embedding is not None:
                    if isinstance(embedding, list) and len(embedding) > 0 and isinstance(embedding[0], list):
                        flat_embedding = [item for sublist in embedding for item in sublist]
                        embedding = flat_embedding
    
                    # If the returned vector length is a multiple of the expected dimension,
                    # assume it contains multiple token embeddings that need pooling.
                    if len(embedding) != self.embedding_dimension and len(embedding) % self.embedding_dimension == 0:
                        n = len(embedding) // self.embedding_dimension
                        # Reshape into a matrix with shape (n, embedding_dimension)
                        embedding_matrix = np.array(embedding).reshape(n, self.embedding_dimension)
                        # Pool across tokens, e.g., by taking the mean
                        pooled_embedding = embedding_matrix.mean(axis=0)
                        embedding = pooled_embedding.tolist()
                    
                    embeddings.append(embedding)
                else:
                    print("Warning: Could not extract embedding from response")
                    embeddings.append([0.0] * self.embedding_dimension)
            
            return embeddings
            
        except Exception as e:
            print(f"Error with SageMaker embedding: {str(e)}")
            # Return zero vectors as fallback
            return [[0.0] * self.embedding_dimension] * len(texts)
