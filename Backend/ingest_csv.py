import os
import re
import chromadb
import ollama
import pandas as pd

# --- Paths ---
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chromadb")
CSV_PATH    = os.path.join(BASE_DIR, "foods2.csv")   # <-- rename your CSV to this

# --- ChromaDB (append into existing collection) ---
client     = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("foods")

# --- Get current count so new IDs don't clash ---
existing_count = collection.count()
print(f"Existing foods in DB: {existing_count}")

# --- Columns we actually want ---
KEEP_COLS = [
    "name", "serving_size", "calories",
    "protein", "carbohydrate", "fat", "fiber", "sugars",
    "saturated_fat", "sodium", "potassium",
    "calcium", "vitamin_c", "vitamin_d", "irom",   # irom = iron (typo in dataset)
    "magnesium", "cholesterol"
]

# --- Helper: strip units from values like "72g", "0.4g", "9.00 mg" ---
def strip_units(val):
    if pd.isna(val):
        return 0.0
    s = str(val).strip()
    # Extract leading number
    m = re.match(r"[\d.]+", s)
    return float(m.group()) if m else 0.0

# --- Embedding function ---
def embed(text: str):
    return ollama.embeddings(model="nomic-embed-text", prompt=text)["embedding"]

# --- Load CSV ---
df = pd.read_csv(CSV_PATH)
print(f"Loaded {len(df)} rows from CSV.")

# --- Normalize column names (lowercase, strip spaces) ---
df.columns = [c.strip().lower() for c in df.columns]

# --- Rename carbohydrate to carbs_g style for consistency ---
rename_map = {
    "carbohydrate": "carbs_g",
    "protein":      "protein_g",
    "fat":          "fat_g",
    "fiber":        "fiber_g",
    "sugars":       "sugar_g",
    "irom":         "iron_mg",       # typo in dataset = iron
    "potassium":    "potassium_mg",
    "calcium":      "calcium_mg",
    "vitamin_c":    "vitamin_c_mg",
    "vitamin_d":    "vitamin_d_iu",
    "magnesium":    "magnesium_mg",
    "cholesterol":  "cholesterol_mg",
    "saturated_fat":"saturated_fat_g",
    "sodium":       "sodium_mg",
}
df = df.rename(columns=rename_map)

# --- Batch settings ---
BATCH_SIZE = 50
ids, embeddings, documents, metadatas = [], [], [], []

for i, row in df.iterrows():
    name         = str(row.get("name", "Unknown")).strip()
    serving      = str(row.get("serving_size", "100g")).strip()
    calories     = strip_units(row.get("calories", 0))
    protein      = strip_units(row.get("protein_g", 0))
    carbs        = strip_units(row.get("carbs_g", 0))
    fat          = strip_units(row.get("fat_g", 0))
    fiber        = strip_units(row.get("fiber_g", 0))
    sugar        = strip_units(row.get("sugar_g", 0))
    sat_fat      = strip_units(row.get("saturated_fat_g", 0))
    sodium       = strip_units(row.get("sodium_mg", 0))
    potassium    = strip_units(row.get("potassium_mg", 0))
    calcium      = strip_units(row.get("calcium_mg", 0))
    vitamin_c    = strip_units(row.get("vitamin_c_mg", 0))
    iron         = strip_units(row.get("iron_mg", 0))
    magnesium    = strip_units(row.get("magnesium_mg", 0))
    cholesterol  = strip_units(row.get("cholesterol_mg", 0))

    # Build embedding text (same style as your original ingest)
    text = (
        f"{name}. "
        f"Serving: {serving}. "
        f"Calories: {calories}. "
        f"Protein: {protein}g. "
        f"Carbs: {carbs}g. "
        f"Fat: {fat}g. "
        f"Fiber: {fiber}g. "
        f"Sugar: {sugar}g. "
        f"Saturated fat: {sat_fat}g. "
        f"Sodium: {sodium}mg. "
        f"Potassium: {potassium}mg. "
        f"Calcium: {calcium}mg. "
        f"Vitamin C: {vitamin_c}mg. "
        f"Iron: {iron}mg. "
        f"Magnesium: {magnesium}mg. "
        f"Cholesterol: {cholesterol}mg."
    )

    metadata = {
        "food_name":       name,
        "serving_size":    serving,
        "calories":        calories,
        "protein_g":       protein,
        "carbs_g":         carbs,
        "fat_g":           fat,
        "fiber_g":         fiber,
        "sugar_g":         sugar,
        "saturated_fat_g": sat_fat,
        "sodium_mg":       sodium,
        "potassium_mg":    potassium,
        "calcium_mg":      calcium,
        "vitamin_c_mg":    vitamin_c,
        "iron_mg":         iron,
        "magnesium_mg":    magnesium,
        "cholesterol_mg":  cholesterol,
        "source":          "dataset2",   # lets you tell the two datasets apart
    }

    emb = embed(text)

    # ID starts after existing entries so there's no clash
    ids.append(str(existing_count + i))
    embeddings.append(emb)
    documents.append(text)
    metadatas.append(metadata)

    if len(ids) == BATCH_SIZE:
        collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        print(f"Inserted up to row {i + 1}...")
        ids, embeddings, documents, metadatas = [], [], [], []

# --- Final batch ---
if ids:
    collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

print(f"✅ DONE. Total foods in DB: {collection.count()}")
