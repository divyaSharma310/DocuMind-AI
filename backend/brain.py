from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Isse .env file load ho jayegi
load_dotenv()

def ask_question(vector_db, query):
    # API Key uthana
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "Error: GROQ_API_KEY nahi mili. .env file check karein."

    # Groq Model (Fastest for Deployment)
    llm = ChatGroq(
        temperature=0, 
        groq_api_key=api_key, 
        model_name="llama-3.3-70b-versatile" 
    )

    template = """
    You are DocuMind AI. Answer based only on context.
    Context: {context}
    Question: {question}
    Answer:"""
    
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    result = qa_chain.invoke({"query": query})
    return result["result"]