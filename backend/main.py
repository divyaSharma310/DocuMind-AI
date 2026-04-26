import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Direct imports work because of ENV PYTHONPATH in Dockerfile
from ingestor import process_pdf
from vector_store import save_to_vector_db, load_vector_db
from brain import ask_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_db = None

@app.get("/")
def home():
    return {"status": "DocuMind AI is Live on Hugging Face"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # Save to current directory in Docker
        file_path = f"./{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks = process_pdf(file_path)
        global vector_db
        vector_db = save_to_vector_db(chunks)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"status": "Success"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.get("/ask")
async def chat(q: str):
    global vector_db
    if vector_db is None:
        try:
            vector_db = load_vector_db()
        except:
            return {"answer": "Please upload a PDF first to start the conversation."}
    
    answer = ask_question(vector_db, q)
    return {"answer": answer}