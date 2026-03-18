# food_search_tool.py
import chromadb
from sentence_transformers import SentenceTransformer

# load embedding model (must match the one used to build DB)
model = SentenceTransformer("all-MiniLM-L6-v2")

# connect to your existing ChromaDB
client = chromadb.PersistentClient(
    path="D:/AM - GRADE 10/P3-Software-Dev/BetterU/Backend/chromadb"
)

print("Using DB path:", client.get_settings().persist_directory)

print("Collections:")
for col in client.list_collections():
    print("-", col.name)
collection = client.get_collection("foods")


def embed_text(text: str):
    return model.encode(text).tolist()


def search_foods(query):
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=3
    )

    foods = []

    for i in range(len(results["documents"][0])):
        metadata = results["metadatas"][0][i]

        food = {
            "name": metadata.get("food_name", "Unknown Food"),
            "calories": metadata.get("calories", 0),
            "protein": metadata.get("protein_g", 0),
            "carbs": metadata.get("carbs_g", 0),
            "fat": metadata.get("fat_g", 0)
        }

        foods.append(food)

    return foods


if __name__ == "__main__":
    q = input("Enter a food query: ")
    res = search_foods(q)
    for r in res:
        print(r)