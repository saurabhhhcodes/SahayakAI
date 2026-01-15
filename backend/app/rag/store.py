import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os

# Initialize persistent client (or in-memory for MVP)
client = chromadb.Client()

# Sample Knowledge Base for MVP (Sunita's Scenario)
docs = [
    Document(
        page_content="Teaching Subtraction with Zero: Use the 'Money Exchange' analogy. 10 Rupees note can be changed into 10 coins of 1 Rupee. Similarly 1 Ten is 10 Ones. Don't say 'borrow', say 'regroup' or 'exchange'.",
        metadata={"topic": "subtraction", "grade": "4", "type": "pedagogy"}
    ),
    Document(
        page_content="Classroom Noise Control: Use a 'Call and Response'. When teacher says 'One Two Three', students say 'Eyes on me'. Make it a game. Reward the quietest row with a star.",
        metadata={"topic": "discipline", "type": "management"}
    ),
    Document(
        page_content="Multi-grade Engagement: Give the older group (Class 5) a self-work worksheet while you teach concepts to the younger group (Class 4). Use peer-learning leaders.",
        metadata={"topic": "multi-grade", "type": "management"}
    )
]

# Simple setup function
def get_vector_store():
    # In a real app, this would load from disk. For MVP, we re-create/load.
    try:
        # Use Open Source Embeddings (runs on CPU, no API key needed)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name="sahayak_knowledge"
        )
        return vectorstore
    except Exception as e:
        print(f"RAG Init Error: {e}")
        return None

def query_rag(query: str, k: int = 2):
    store = get_vector_store()
    if not store:
        return "No Context Available (Offline/Mock Mode)"
        
    results = store.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results])
