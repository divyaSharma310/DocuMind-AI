import os
from langchain_groq import ChatGroq # Isko verify ke liye rakha hai
from langchain_community.vectorstores import Chroma
# Naya import path jo har version mein kaam karta hai
from langchain_community.embeddings import DeterministicFakeEmbedding 
from langchain_groq import GroqEmbeddings
import shutil
from dotenv import load_dotenv

load_dotenv()

# Cloud Embeddings
embeddings = GroqEmbeddings(
    model_name="nomic-embed-text-v1.5",
    groq_api_key=os.getenv("GROQ_API_KEY")
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