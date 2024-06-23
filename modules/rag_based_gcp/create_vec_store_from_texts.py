import os

from langchain_google_vertexai import (
    VectorSearchVectorStore,
    VectorSearchVectorStoreDatastore,
)
from langchain_google_vertexai import VertexAIEmbeddings
import dotenv
dotenv.load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")
BUCKET = os.getenv("BUCKET")

embedding_model = VertexAIEmbeddings(model_name="textembedding-gecko@003")


input_texts = []
vector_store = VectorSearchVectorStore.from_components(
    project_id=PROJECT_ID,
    region=REGION,
    gcs_bucket_name=BUCKET,
    index_id="",
    endpoint_id="",
    embedding=embedding_model,
    stream_update=True,
)

vector_store.add_texts(input_texts)
vector_store.similarity_search()
