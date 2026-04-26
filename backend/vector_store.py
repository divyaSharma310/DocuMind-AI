import os
import shutil
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_community.vectorstores import FAISS

# API based embeddings - Uses 0 RAM
embeddings = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    huggingfacehub_api_token=os.getenv("HF_TOKEN")
)

def save_to_vector_db(chunks):
    # FAISS is just a folder, easy to delete and recreate
    if os.path.exists("./faiss_index"):
        shutil.rmtree("./faiss_index")
    
    vector_db = FAISS.from_documents(chunks, embeddings)
    vector_db.save_local("./faiss_index")
    return vector_db

def load_vector_db():
    return FAISS.load_local("./faiss_index", embeddings, allow_dangerous_deserialization=True)