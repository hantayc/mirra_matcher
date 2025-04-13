from pinecone import Pinecone

PINECONE_API_KEY = (
    "pcsk_7VkStS_ifR3SH9d1MSkkju9kP7DUt5M16CpNyzi9dwNBm7iUqyXmbKZWQbC55ZzfSEaAB"
)
PINECONE_ENVIRONMENT = "us-east-1"
PINECONE_INDEX_NAME = "sample-100-strings" 

try:
    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)
    print("Pinecone connected successfully!")
except Exception as e:
    # If any error occurs, print it and fallback to None
    print("Error connecting to Pinecone, proceeding without it:", str(e))
    pc = None
    pinecone_index = None

embedding_cache = {}
similarity_cache = {}
aggregated_candidate_cache = {}
pinecone_query_cache = {}
faiss_index_cache = {}