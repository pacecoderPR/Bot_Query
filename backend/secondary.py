import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import weaviate
from weaviate.classes.init import Auth
import re
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Get sensitive data from the environment
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
CLUSTER_URL = os.getenv("CLUSTER_URL")

if not API_KEY or not SECRET_KEY or not CLUSTER_URL:
    raise EnvironmentError(
        "API_KEY, SECRET_KEY, or CLUSTER_URL is missing from environment variables."
    )

# Initialize Weaviate client
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=CLUSTER_URL,  # Environment variable
    auth_credentials=Auth.api_key(API_KEY),
    skip_init_checks=True,
)

# Initialize the collection
dbuse = client.collections.get("testcheck")

# Initialize FastAPI app
app = FastAPI()

# Set up CORS middleware
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


# Initialize SentenceTransformer model
embedding_model = SentenceTransformer("paraphrase-MiniLM-L3-v2")


# Function to generate embeddings
def generate_embeddings_batch(text_chunks, batch_size=32):
    embeddings = []
    for i in range(0, len(text_chunks), batch_size):
        batch = text_chunks[i : i + batch_size]
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

def preprocess_html(html):
  
    soup = BeautifulSoup(html, "html.parser")

    # Remove script and style elements
    for tag in soup(["script", "style"]):
        tag.decompose()

   

    return soup

def clean_text(text):
    cleaned_text = text.replace("\n", " ").replace("\r", "")
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    return cleaned_text
    
async def batch_insert_to_weaviate(chunks, embeddings, source_url, batch_size=50):
    batch_data = []
    for idx, chunk in enumerate(chunks):
        batch_data.append({
            "text": chunk,
            "source_url": source_url,
            "vector": embeddings[idx].tolist(),
        })

        if len(batch_data) >= batch_size:
            dbuse.data.insert_batch(properties=batch_data)
            batch_data = []

    if batch_data:
        dbuse.data.insert_batch(properties=batch_data)
def get_html_for_match(match, chunk_to_html_mapping):
    """
    This function will find the corresponding HTML for a given match.
    It will return the HTML or 'No HTML found' if no mapping is found.
    """
    # Look for a match, ensuring we compare the text case-insensitively and ignore leading/trailing spaces.
    match_html = next(
        (
            mapping["html"]
            for mapping in chunk_to_html_mapping
            if mapping["chunk"].strip().lower() == match.strip().lower()
        ),
        None  # If not found, return None
    )
    
    # If no match is found, return a default value
    if match_html is None:
        print(f"Warning: No HTML found for match: {match}")
        return "No matching HTML"  # Default value when no match is found
    
    return match_html
def process_matches(top_matches, chunk_to_html_mapping):
    results = []
    
    for match in top_matches:
        cleaned_match = clean_text(match)
        match_html = get_html_for_match(match, chunk_to_html_mapping)
        
        # Add the cleaned match and its HTML to the results list
        results.append({"text": cleaned_match, "html": match_html})
    
    return results
@app.post("/search")
async def search(request: SearchRequest):
    try:
        # Fetch content from the provided URL
        response = requests.get(request.url)

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch content.")

        # Parse the response HTML and extract text
        soup = BeautifulSoup(response.text, "html.parser")
        soup = preprocess_html(response.text)

        # Collect text with its HTML position
        html_content = []
        for elem in soup.find_all(True):  # Find all HTML elements
            element_text = elem.get_text(strip=True)
            if element_text:  # Only keep elements with actual text
                html_content.append({"html": str(elem), "text": element_text})
        # print(html_content)
        # Concatenate text to form the complete text for splitting
        full_text = " ".join(item["text"] for item in html_content)
        

        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=50)
        text_chunks = text_splitter.split_text(full_text)

        # Precompute positions for html_content
        # Precompute start and end positions of each HTML element in the full_text
        html_positions = []
        current_index = 0

        for item in html_content:
            start_index = current_index
            end_index = start_index + len(item["text"])
            html_positions.append({"start": start_index, "end": end_index, "html": item["html"]})
            current_index = end_index

    # Map chunks to HTML without repetitive find
        chunk_to_html_mapping = []
        text_cursor = 0

        for chunk in text_chunks:
            chunk_length = len(chunk)
            chunk_start = text_cursor
            chunk_end = chunk_start + chunk_length

            # Collect all HTML elements falling within the chunk's range
            relevant_html = [
                pos["html"]
                for pos in html_positions
                if not (pos["end"] <= chunk_start or pos["start"] >= chunk_end)  # Overlap check
            ]
        
        chunk_to_html_mapping.append({"chunk": chunk, "html": relevant_html})
        text_cursor = chunk_end


        # print(chunk_to_html_mapping)
        print(len(text_chunks))
        # Generate embeddings for the text chunks
        
        chunk_embeddings = generate_embeddings_batch(text_chunks)
        query_embedding = embedding_model.encode([request.query])[0]
        print(query_embedding)

        # Insert data into Weaviate
        for idx, chunk in enumerate(text_chunks):
            dbuse.data.insert(
                properties={
                    "text": chunk,
                    "source_url": request.url,
                    "vector": chunk_embeddings[idx].tolist(),
                }
            )
       
        # Generate embeddings for the search query
       
       
        # Retrieve vectors and content from Weaviate
        embedded_database_vector = []
        db_content = []
        for item in dbuse.iterator():
            if item.properties.get("vector") is not None:
                embedded_database_vector.append(item.properties.get("vector"))
                db_content.append(item.properties.get("text"))

        # Find the top matches using cosine similarity
        top_matches = nearBy(
            embedded_database_vector,
            query_embedding,
            top_n=10,
            db_content=db_content,
        )
        print(chunk_to_html_mapping)
        # Clean the matches and map them back to the relevant HTML
        # for match in top_matches:
        #     cleaned_match = clean_text(match)
        #     match_html = next(
        #         (
        #             mapping["html"]
        #             for mapping in chunk_to_html_mapping
        #             if mapping["chunk"] == match
        #         ),
        #         None,
        #     )
        #     results.append({"text": cleaned_match, "html": match_html})
        results = process_matches(top_matches, chunk_to_html_mapping)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

    