import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Robust imports
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

# Global variable
vector_db = None

@app.get("/")
def home():
    return {"status": "DocuMind AI is Live"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global vector_db
    # Using /tmp for the uploaded file as well
    temp_path = f"/tmp/{file.filename}"
    
    print(f"--- STARTING UPLOAD: {file.filename} ---")
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks = process_pdf(temp_path)
        vector_db = save_to_vector_db(chunks)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        print("--- UPLOAD COMPLETE: SUCCESS ---")
        return {"status": "Success"}
    except Exception as e:
        print(f"--- UPLOAD FAILED: {str(e)} ---")
        return {"status": "Error", "message": str(e)}

@app.get("/ask")
async def chat(q: str):
    global vector_db
    
    # SENIOR LOGIC: If variable is empty, try loading from the guaranteed /tmp folder
    if vector_db is None:
        print("--- RAM empty, checking /tmp/faiss_index ---")
        try:
            vector_db = load_vector_db()
            print("--- Success: Brain recovered from disk ---")
        except Exception as e:
            print(f"--- Recovery failed: {str(e)} ---")
            return {"answer": "I don't have any documents in my memory. Please upload a PDF and wait for the 'Success' message."}
    
    try:
        answer = ask_question(vector_db, q)
        return {"answer": answer}
    except Exception as e:
        print(f"--- AI ERROR: {str(e)} ---")
        return {"answer": f"AI encountered an error: {str(e)}"}

if __name__ == "__main__":
    # HF uses port 7860
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)