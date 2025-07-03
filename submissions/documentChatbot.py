from read_env import *
import langchain
langchain.verbose = False

# Import required LangChain modules
from langchain.document_loaders import PyPDFLoader,Docx2txtLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import pickle
from langchain.chains import RetrievalQA
from langchain.agents import Tool
from QnAtool import *

def tutorial_agent_astool(tutorial_doc_name,query):
    '''
    This function enables question-answering capabilities on unstructured tutorial documents 
    (e.g., PDFs or Word documents containing Python tutorials like those from W3Schools).
    
    The function loads the document, splits the content into manageable text chunks, 
    builds a FAISS vectorstore using embeddings, and returns a tool capable of handling queries.

    Parameters:
        tutorial_doc_name (str): The name of the tutorial file (without extension) located in the "PDFS" folder.

    Returns:
        Tool: A LangChain tool object that can be used for querying the content of the document.
    '''
    file_path_pdf = rf'PDFS\{tutorial_doc_name}.pdf'
    file_path_docx = rf'PDFS\{tutorial_doc_name}.docx'

    # Decide loader based on file extension
    if os.path.exists(file_path_pdf):
        loader = PyPDFLoader(file_path_pdf)
    elif os.path.exists(file_path_docx):
        loader = Docx2txtLoader(file_path_docx)
    else:
        raise FileNotFoundError("Neither .pdf nor .docx file found for the given document name.")
        
    # Load and split the document into pages
    pages = loader.load_and_split()

    # Split the pages into smaller chunks to make them suitable for vector-based retrieval
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(pages)

    # Generate vector embeddings and create a FAISS index
    embeddings = EMBEDDINGS_MODEL
    print("Embeddings created",embeddings)
    retriever = FAISS.from_documents(docs, embeddings).as_retriever()

    # Define the chain to process user queries
    llm = LLM_MODEL_GPT3
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=retriever)
    return qa.run(query)

