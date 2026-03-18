# ask_llm.py
import os
from sentence_transformers import SentenceTransformer
import chromadb
import ollama

# --- Absolute path to your chromadb folder ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chromadb")

# --- Connect to persistent ChromaDB ---
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Use get_or_create_collection to be safe
collection = client.get_or_create_collection("foods")

# --- Load embedding model ---
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    """Generate embedding for a query using MiniLM-L6-v2"""
    return model.encode(text).tolist()

def search_foods(query: str, n_results: int = 5):
    """Search ChromaDB for top N foods relevant to the query"""
    embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    foods = []
    for doc, meta in zip(documents, metadatas):
        foods.append({"text": doc, "metadata": meta})
    return foods

def ask_llm(query: str, n_results: int = 5):
    """Retrieve foods and generate an Ollama answer"""
    results = search_foods(query, n_results=n_results)

    # format context for AI
    context = "\n".join([f"{r['metadata'].get('name', '')}: {r['metadata'].get('description','')}" for r in results])

    response = ollama.chat(
        model="llama3",  # change if using a different Ollama LLM
        messages=[
            {
                "role": "system",
                "content": "You are a food expert. Use the following foods to answer accurately."
            },
            {
                "role": "user",
                "content": f"""
User query: {query}

Relevant foods:
{context}

Answer:
"""
            }
        ]
    )

    return response["message"]["content"]

# --- Interactive test ---
if __name__ == "__main__":
    while True:
        query = input("\nAsk me about foods (or type 'exit'): ").strip()
        if query.lower() == "exit":
            break
        answer = ask_llm(query)
        print("\nAI answer:\n")
        print(answer)