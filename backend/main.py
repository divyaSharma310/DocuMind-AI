import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Force direct imports for Docker
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

# Global database reference
current_db = None

@app.get("/")
def home():
    return {"status": "DocuMind-AI is ready"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    global current_db
    temp_path = os.path.join("/tmp", file.filename) # /tmp is safer for Docker
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"Processing file: {file.filename}")
        chunks = ingestor.process_pdf(temp_path)
        current_db = vector_store.save_to_vector_db(chunks)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return {"status": "Success"}
    except Exception as e:
        print(f"Server-side Upload Error: {str(e)}")
        return {"status": "Error", "message": str(e)}

@app.get("/ask")
async def chat(q: str):
    global current_db
    
    # Auto-recovery if global variable was cleared
    if current_db is None:
        print("RAM empty. Checking disk...")
        current_db = vector_store.load_vector_db()

    if current_db is None:
        return {"answer": "The AI memory is empty. Please upload a PDF file and wait for the Success message."}
    
    try:
        answer = brain.ask_question(current_db, q)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"AI Error: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)