import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# DO NOT use "from backend.ingestor", use exactly this:
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
def health():
    return {"status": "online"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"
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
            raise HTTPException(status_code=400, detail="Database not initialized")
    
    answer = ask_question(vector_db, q)
    return {"answer": answer}