import os
import shutil

# --- CRITICAL RENDER FIX FOR CHROMA ---
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# --------------------------------------

from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import Chroma

# Using HuggingFace API to stay under 512MB RAM
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=os.getenv("HF_TOKEN")
)

def save_to_vector_db(chunks):
    if os.path.exists("./db_storage"):
        shutil.rmtree("./db_storage")
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory="./db_storage"
    )
    return vector_db

def load_vector_db():
    return Chroma(persist_directory="./db_storage", embedding_function=embeddings)