import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Absolute path imports
from ingestor import process_pdf
from vector_store import save_to_vector_db, load_vector_db
from brain import ask_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared global state
vector_db = None

@app.get("/")
def home():
    return {"status": "DocuMind AI Live"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global vector_db
    temp_path = os.path.join(os.getcwd(), file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks = process_pdf(temp_path)
        # 1. Save to RAM
        vector_db = save_to_vector_db(chunks)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {"status": "Success"}
    except Exception as e:
        print(f"UPLOAD ERROR: {str(e)}")
        return {"status": "Error", "message": str(e)}

@app.get("/ask")
async def chat(q: str):
    global vector_db
    
    # RELOAD LOGIC: If variable is None, physically try to load it from the disk
    if vector_db is None:
        print("DEBUG: Global variable empty. Attempting disk recovery...")
        vector_db = load_vector_db()

    if vector_db is None:
        return {"answer": "I don't have any documents in my memory. Please index a PDF first."}
    
    try:
        answer = ask_question(vector_db, q)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"AI Generation Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    # Run with 1 worker to ensure global variables stay consistent
    uvicorn.run("main:app", host="0.0.0.0", port=port, workers=1)