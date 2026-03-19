# ingest.py
import os
import json
import chromadb
import ollama

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chromadb")
JSON_PATH = os.path.join(BASE_DIR, "foods.json")  # <-- your JSON file

# --- Initialize ChromaDB ---
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("foods")

# --- Embedding function using Ollama ---
def embed(text):
    return ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )["embedding"]

# --- Load JSON dataset ---
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} foods from JSON.")

# --- Batch settings ---
batch_size = 50

ids, embeddings, documents, metadatas = [], [], [], []

for i, item in enumerate(data):
    # --- Safely extract fields ---
    name = item.get("food_name", "Unknown Food")
    category = item.get("food_category", "")
    food_type = item.get("food_type", "")

    calories = item.get("calories", 0)
    protein = item.get("protein_g", 0)
    carbs = item.get("carbs_g", 0)
    fat = item.get("fat_g", 0)
    fiber = item.get("fiber_g", 0)
    sugar = item.get("sugar_g", 0)
    health = item.get("health_score", 0)

    # --- Build embedding text ---
    text = (
        f"{name}. "
        f"{food_type} in category {category}. "
        f"Calories: {calories}. "
        f"Protein: {protein}g. "
        f"Carbs: {carbs}g. "
        f"Fat: {fat}g. "
        f"Fiber: {fiber}g. "
        f"Sugar: {sugar}g. "
        f"Health score: {health}."
    )

    emb = embed(text)

    ids.append(str(i))
    embeddings.append(emb)
    documents.append(text)
    metadatas.append(item)

    # --- Batch insert into ChromaDB ---
    if len(ids) == batch_size:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Inserted {i + 1} foods...")
        ids, embeddings, documents, metadatas = [], [], [], []

# --- Insert remaining batch ---
if ids:
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

print("✅ DONE: All foods ingested into ChromaDB.")