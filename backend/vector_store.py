import os
import shutil
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# Absolute path for Docker persistence
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = "/tmp/faiss_data" # Using /tmp for guaranteed write access

# SENIOR FIX: Loading the model LOCALLY inside the container. 
# This bypasses the "Expecting value" API error entirely.
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="/tmp/models"
)

def save_to_vector_db(chunks):
    try:
        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        
        print(f"DEBUG: Running local embeddings for {len(chunks)} chunks...")
        vector_db = FAISS.from_documents(chunks, embeddings)
        
        print(f"DEBUG: Saving FAISS index to {DB_PATH}")
        vector_db.save_local(DB_PATH)
        return vector_db
    except Exception as e:
        print(f"CRITICAL ERROR IN VECTOR STORE: {str(e)}")
        raise e

def load_vector_db():
    if not os.path.exists(DB_PATH):
        print(f"DEBUG: No index found at {DB_PATH}")
        return None
    
    print("DEBUG: Loading FAISS index into memory.")
    return FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)