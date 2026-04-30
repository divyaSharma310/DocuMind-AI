import os
import shutil
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# SENIOR FIX: Use /tmp for guaranteed write access in Docker containers
DB_PATH = "/tmp/faiss_index"

hf_token = os.getenv("HF_TOKEN")

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=hf_token
)

def save_to_vector_db(chunks):
    print(f"--- System: Cleaning old index at {DB_PATH} ---")
    try:
        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        
        print(f"--- System: Creating new FAISS index ---")
        vector_db = FAISS.from_documents(chunks, embeddings)
        
        # Save to the guaranteed /tmp path
        vector_db.save_local(DB_PATH)
        print(f"--- System: Index successfully saved to {DB_PATH} ---")
        return vector_db
    except Exception as e:
        print(f"--- FAISS SAVE ERROR: {str(e)} ---")
        raise e

def load_vector_db():
    print(f"--- System: Attempting to load index from {DB_PATH} ---")
    if not os.path.exists(DB_PATH):
        print("--- System Error: DB_PATH does not exist ---")
        raise Exception("Index folder missing")
    
    return FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)