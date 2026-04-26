from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

def ask_question(vector_db, query):
    # Groq Llama 3 - Free and Fast
    llm = ChatGroq(
        temperature=0, 
        groq_api_key=os.getenv("GROQ_API_KEY"), 
        model_name="llama-3.3-70b-versatile"
    )

    template = """
    You are DocuMind AI, an expert document assistant.
    Use the following pieces of context to answer the user's request.
    If the answer is not in the context, say "I don't have enough data in this document."

    Context: {context}
    Question: {question}
    
    Helpful Answer:"""
    
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