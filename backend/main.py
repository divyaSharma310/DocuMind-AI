import pysqlite3
import sys
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")




from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
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
if os.path.exists("./db_storage"):
    try:
        vector_db = load_vector_db()
        print("Existing Knowledge Base Loaded!")
    except:
        vector_db = None

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks = process_pdf(file_path)
        global vector_db
        vector_db = save_to_vector_db(chunks)
        os.remove(file_path)
        
        return {"status": "Success", "message": f"{file.filename} indexed!"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.get("/ask")
async def chat(q: str):
    global vector_db
    if vector_db is None:
        return {"answer": "Pehle koi PDF upload karein taaki main usey samajh sakun."}
    
    answer = ask_question(vector_db, q)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)