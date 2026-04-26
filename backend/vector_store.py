from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

# Free embedding model used for production
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def save_to_vector_db(chunks):
    # Clear existing database to save space and prevent conflicts on Render
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