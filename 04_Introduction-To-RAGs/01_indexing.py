import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_opendataloader_pdf import OpenDataLoaderPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

pdf_path = Path(__file__).parent / "js-intro.pdf"

# loading data 
loader = OpenDataLoaderPDFLoader(
    file_path=pdf_path,
    format="text",
)

documents = loader.load()

# chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)

texts = text_splitter.split_documents(documents)

# vector embeddings

embedding_model = OpenAIEmbeddings(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model="gemini-embedding-001",
    tiktoken_enabled=False,
    check_embedding_ctx_length=False,
)

# using [embedding_model], create vector embeddings of [texts] and store in DB
vector_store = QdrantVectorStore.from_documents(
    documents=texts,
    url="http://localhost:6333",
    collection_name="learning_vector",
    embedding=embedding_model,
)

print("Indexing of documents done")