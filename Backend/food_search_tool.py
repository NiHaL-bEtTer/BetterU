# food_search_tool.py
import chromadb
from sentence_transformers import SentenceTransformer

# load embedding model (must match the one used to build DB)
model = SentenceTransformer("all-MiniLM-L6-v2")

# connect to your existing ChromaDB
client = chromadb.PersistentClient(path="Backend/chromadb")
collection = client.get_collection("foods")


def embed_text(text: str):
    return model.encode(text).tolist()


def search_foods(query: str, n_results: int = 5):
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


if __name__ == "__main__":
    q = input("Enter a food query: ")
    res = search_foods(q)
    for r in res:
        print(r)