import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

embedding_model = OpenAIEmbeddings(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    model="gemini-embedding-001",
    tiktoken_enabled=False,
    check_embedding_ctx_length=False,
)

existing_vector_db = QdrantVectorStore.from_existing_collection(
    url="http://vector-db:6333",
    collection_name="learning_vector",
    embedding=embedding_model,
)

async def process_query(query: str) : 
    print("Searching chunks in the vector db for query:", query)
    
    search_similar_vectors = existing_vector_db.similarity_search(
        query=query,
    )
    
    context = "\n".join([f"Page content: {results.page_content}\n Page number: {results.metadata.get("page")}" for results in search_similar_vectors])

    SYSTEM_PROMPT = f"""
        you are a helpful AI assistant specialized in resolving user query.
        you are given certain information/data about the user query in the form of metadata, retrived from a pdf file along with page number.

        you have to analyse the information and extract the most relevant data related to the query.

        you should only answer based on the extracted information and you can also navigate the user on the correct page numbers.

        refer to this context : {context}

        you have to draft a response according to the relevant information, ensuring it resolves the user's query.

        you can also ask a follow-up question to the user related to the query.
    """
    
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            { "role": "user", "content": query},
        ]
    )

    print("🤖 Response:", response.choices[0].message.content, "\n\n\n")
    return response.choices[0].message.content