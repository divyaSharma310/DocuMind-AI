import os
import shutil
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# SENIOR FIX: Use absolute path for Docker/HF environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "faiss_index")

hf_token = os.getenv("HF_TOKEN")

embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=hf_token
)

def save_to_vector_db(chunks):
    print(f"--- System: Saving to {DB_PATH} ---")
    try:
        if os.path.exists(DB_PATH):
            shutil.rmtree(DB_PATH)
        
        vector_db = FAISS.from_documents(chunks, embeddings)
        vector_db.save_local(DB_PATH)
        return vector_db
    except Exception as e:
        print(f"--- FAISS Error: {str(e)} ---")
        raise e

def load_vector_db():
    # If not in RAM, physically look for the folder
    if not os.path.exists(DB_PATH):
        raise Exception("Index folder missing")
    return FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)