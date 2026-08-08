import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    collection_name="user_memories",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

def add_memory(memory_id: int, user_id: str, content: str):
    vector_store.add_texts(
        texts=[content],
        metadatas=[{"user_id": user_id}],
        ids=[str(memory_id)]
    )

def search_memories(user_id: str, query: str, k: int = 3):
    results = vector_store.similarity_search(
        query,
        k=k,
        filter={"user_id": user_id}
    )

    return results