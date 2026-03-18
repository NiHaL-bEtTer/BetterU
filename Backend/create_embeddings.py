import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm

# -----------------------------
# PATHS
# -----------------------------

FOOD_DATA_PATH = r"D:\AM - GRADE 10\P3-Software-Dev\BetterU\Data\foods.json"

CHROMA_DB_PATH = r"D:\AM - GRADE 10\P3-Software-Dev\BetterU\Backend\chromadb"

COLLECTION_NAME = "foods"

# -----------------------------
# CREATE DATABASE FOLDER
# -----------------------------

os.makedirs(CHROMA_DB_PATH, exist_ok=True)

print("ChromaDB folder:", CHROMA_DB_PATH)

# -----------------------------
# LOAD FOOD DATA
# -----------------------------

with open(FOOD_DATA_PATH, "r", encoding="utf-8") as f:
    foods = json.load(f)

print("Foods loaded:", len(foods))

# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# CONNECT TO CHROMA
# -----------------------------

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

# -----------------------------
# CREATE EMBEDDINGS
# -----------------------------

BATCH_SIZE = 4000

print("Creating embeddings and storing in vector DB...")

for i in tqdm(range(0, len(foods), BATCH_SIZE)):

    batch = foods[i:i+BATCH_SIZE]

    ids = []
    docs = []
    embeddings = []
    metadata = []

    for j, food in enumerate(batch):

        text = f"""
        {food['food_name']}
        category: {food['food_category']}
        calories: {food['calories']}
        protein: {food['protein_g']}
        carbs: {food['carbs_g']}
        fat: {food['fat_g']}
        fiber: {food['fiber_g']}
        sugar: {food['sugar_g']}
        sodium: {food['sodium_mg']}
        """

        emb = model.encode(text).tolist()

        ids.append(str(i + j))
        docs.append(text)
        embeddings.append(emb)
        metadata.append(food)

    collection.add(
        ids=ids,
        documents=docs,
        embeddings=embeddings,
        metadatas=metadata
    )

print("✅ Food vector database successfully created.")
print("Location:", CHROMA_DB_PATH)