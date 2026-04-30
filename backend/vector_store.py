import os
import shutil
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# Absolute path for Docker
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "faiss_data")

# Critical: Using the stable Inference API wrapper
embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HF_TOKEN"),
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def save_to_vector_db(chunks):
    try:
        # Create directory if not exists
        if not os.path.exists(DB_PATH):
            os.makedirs(DB_PATH)
        else:
            shutil.rmtree(DB_PATH)
            os.makedirs(DB_PATH)
        
        print(f"DEBUG: Generating embeddings and saving to {DB_PATH}")
        vector_db = FAISS.from_documents(chunks, embeddings)
        vector_db.save_local(DB_PATH)
        print("DEBUG: FAISS saved successfully.")
        return vector_db
    except Exception as e:
        print(f"CRITICAL ERROR SAVING FAISS: {str(e)}")
        raise e

def load_vector_db():
    if not os.path.exists(DB_PATH) or not os.path.exists(os.path.join(DB_PATH, "index.faiss")):
        print(f"DEBUG: DB_PATH not found at {DB_PATH}")
        return None
    
    print("DEBUG: Loading FAISS from disk.")
    return FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)