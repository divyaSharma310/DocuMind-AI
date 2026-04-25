from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

# Free embedding model (Ye cloud par bhi bilkul free chalta hai)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def save_to_vector_db(chunks):
    # Purana data saaf karna taaki naye file mein confusion na ho
    if os.path.exists("./db_storage"):
        shutil.rmtree("./db_storage")
        
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        
        persist_directory="./db_storage"
    )
    return vector_db

def load_vector_db():
    # Database load karne ka function
    return Chroma(persist_directory="./db_storage", embedding_function=embeddings)