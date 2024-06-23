# load the environment variables
import os

from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
BUCKET = os.getenv("BUCKET")
BUCKET_URI = f"gs://{BUCKET}"
DIMENSIONS = int(os.getenv("DIMENSIONS"))
INDEX_NAME = os.getenv("INDEX_NAME")
INDEX_ID = os.getenv("INDEX_ID")

from google.cloud import aiplatform
from langchain_google_vertexai import VertexAIEmbeddings
aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)
embedding_model = VertexAIEmbeddings(model_name='textembedding-gecko@003')

# create an empty index
my_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name='index_from_py_code',
    dimensions=768,
    approximate_neighbors_count=150,
    distance_measure_type='DOT_PRODUCT_DISTANCE', # 点积距离
    index_update_method='STREAM_UPDATE',
)

# create an endpoint
my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name='index_from_py_code_endpoint',
    public_endpoint_enabled=True,
)

# deploy index to the endpoint
my_index_endpoint = my_index_endpoint.deploy_index(
    index= my_index,
    deployed_index_id="index_from_py_code_endpoint_id",
)



