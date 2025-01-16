import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import weaviate
import re
from weaviate.classes.init import Auth
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Get API_KEY, SECRET_KEY, and CLUSTER_URL from the environment
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
CLUSTER_URL = os.getenv("CLUSTER_URL")

# Initialize Weaviate client
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=CLUSTER_URL,  # Now using environment variable
    auth_credentials=Auth.api_key(API_KEY),
    skip_init_checks=True
)

# Create a Weaviate collection (similar to creating an index in Pinecone)
dbuse = client.collections.get("testcheck")

# Initialize FastAPI app
app = FastAPI()

# Set up CORS middleware to allow communication from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define incoming request body structure
class SearchRequest(BaseModel):
    url: str
    query: str

# Initialize SentenceTransformer
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to generate embeddings
def generate_embeddings_batch(text_chunks, batch_size=32):
    embeddings = []
    for i in range(0, len(text_chunks), batch_size):
        batch = text_chunks[i:i + batch_size]
        batch_embeddings = embedding_model.encode(batch, convert_to_tensor=False)
        embeddings.extend(batch_embeddings)
    return embeddings

def nearBy(embedded_database_vector, query_embedding, top_n=10, db_content=None):
    query_embedding = np.array(query_embedding).reshape(1, -1)
    embedded_database_vector = np.array(embedded_database_vector)
    similarities = cosine_similarity(query_embedding, embedded_database_vector)
    top_indices = similarities[0].argsort()[-top_n:][::-1]
    top_matches = [db_content[i] for i in top_indices]
    return top_matches

def clean_text(text):
    cleaned_text = text.replace("\n", " ").replace("\r", "")
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

@app.post("/search")
async def search(request: SearchRequest):
    try:
        response = requests.get(request.url)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch content.")

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_chunks = text_splitter.split_text(text)

        chunk_embeddings = generate_embeddings_batch(text_chunks)
        print(len(text_chunks))
        for idx, chunk in enumerate(text_chunks):
            dbuse.data.insert(
                properties={
                    "text": chunk,
                    "source_url": request.url,
                    "vector": chunk_embeddings[idx].tolist()
                })

        query_embedding = embedding_model.encode([request.query])[0]
        embedded_database_vector = []
        db_content = []

        for item in dbuse.iterator():
            if item.properties.get('vector') is not None:
                embedded_database_vector.append(item.properties.get('vector'))
                db_content.append(item.properties.get('text'))
        
        top_matches = nearBy(embedded_database_vector, query_embedding, top_n=10, db_content=db_content)
        cleaned_top_matches = [clean_text(match) for match in top_matches]
        return cleaned_top_matches

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))