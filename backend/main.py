import os
from dotenv import load_dotenv
load_dotenv()
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA

app = FastAPI()

# --- Configuration ---
INDEX_PATH = "faiss_index"
UPLOAD_DIR = "temp_files"
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")

class QueryRequest(BaseModel):
    question: str

# --- Helper: Indexing Logic ---
def process_and_index_file(file_path):
    # 1. Load the file
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
    
    documents = loader.load()
    
    # 2. Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    
    # 3. Add to or Create VectorStore
    if os.path.exists(INDEX_PATH):
        vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(splits)
    else:
        vectorstore = FAISS.from_documents(splits, embeddings)
        
    vectorstore.save_local(INDEX_PATH)
    print(f"File {file_path} indexed successfully!")

# --- Helper: Query Logic ---
def ask_ai(question: str):
    # 1. Load the vectorstore (The "Book" of your files)
    if not os.path.exists(INDEX_PATH):
        return "Knowledge base is empty. Please upload files first."
        
    vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    
    # 2. Setup the LLM (Gemini)
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    # 3. Create the Retrieval Chain
    # This automatically finds relevant info from your files and sends it to the LLM
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever()
    )
    
    # 4. Get the answer
    result = qa_chain.invoke(question)
    return result["result"]

# --- Endpoints ---
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        process_and_index_file(file_location)
        return {"message": f"File {file.filename} indexed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    answer = ask_ai(request.question)
    return {"answer": answer}