import os
import chromadb

# absolute path to your chromadb folder
CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromadb")

print("Using ChromaDB path:", CHROMA_PATH)

client = chromadb.PersistentClient(path=CHROMA_PATH)

print("Collections in this DB:")
for c in client.list_collections():
    print("-", c.name)

# try to get the collection
try:
    collection = client.get_collection("foods")
    print("Successfully retrieved collection:", collection.name)
except Exception as e:
    print("Error retrieving collection:", e)