import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import ingestor
import vector_store
import brain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

current_db = None

@app.get("/")
def home():
    return {"status": "DocuMind AI is Live and Healthy"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global current_db
    temp_path = os.path.join("/tmp", file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"--- Action: Processing {file.filename} ---")
        chunks = ingestor.process_pdf(temp_path)
        current_db = vector_store.save_to_vector_db(chunks)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        print("--- Status: Success ---")
        return {"status": "Success"}
    except Exception as e:
        print(f"--- Fatal Upload Error: {str(e)} ---")
        return {"status": "Error", "message": str(e)}

@app.get("/ask")
async def chat(q: str):
    global current_db
    
    # Check disk if RAM is empty
    if current_db is None:
        current_db = vector_store.load_vector_db()

    if current_db is None:
        return {"answer": "I don't have any documents in my memory. Please upload a PDF and wait for the Success message."}
    
    try:
        answer = brain.ask_question(current_db, q)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"AI Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)