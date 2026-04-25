from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Chunk size badha di taaki AI ko ek baar mein zyada context mile 
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(pages)
    return chunks