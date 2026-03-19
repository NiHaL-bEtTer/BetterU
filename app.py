import os # here we inmport the os, json, chromadb, ollama, fastapi, HTMLResponse, StreamingResponse, CORSMiddleware, BaseModel
import json # json for loading the food dataset
import chromadb # our vecror database
import ollama # our local llm
from fastapi import FastAPI # connecting backend to the frontend
from fastapi.responses import HTMLResponse, StreamingResponse # for serving the frontend and streaming responses
from fastapi.middleware.cors import CORSMiddleware # to allow cross-origin requests from our frontend
from pydantic import BaseModel # for defining request schemas





# here we are configuring the paths the models and the number of results to retrieve from the vector database
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # base directory of the project
CHROMA_PATH = os.path.join(BASE_DIR, "chromadb") # path to the chromadb directory where the vector database is stored
EMBED_MODEL = "nomic-embed-text" # embedding model to use for vectorizing queries
CHAT_MODEL = "llama3"   # we are setting our local llm model to llama 3 8 billion
N_RESULTS = 6             # retrieve top 6 results from the vector database for each query

# this is for the cromadb client to connect to the persistent database we created in the injest.py file and get the "foods" collection which contains our food data
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH) # chroma client is the persisted data base that is stored in the chromadb directory
collection = chroma_client.get_collection("foods") # we get the 

# here we are setting up fast api 
app = FastAPI() # creating an instance of fastapi which is a class that the frontend will interact with for requests



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Serve frontend ---
# --- Serve frontend ---
FRONTEND_PATH = os.path.join(BASE_DIR, "..", "Frontend", "chat.html")

@app.get("/", response_class=HTMLResponse)
def root():
    with open(FRONTEND_PATH, "r") as f:
        return f.read()

# --- Request model ---
class ChatRequest(BaseModel):
    message: str
    history: list = []   # list of {"role": "user"|"assistant", "content": "..."}

# --- Embed query ---
def embed_query(text: str):
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]

# --- RAG retrieval ---
def retrieve(query: str):
    emb = embed_query(query)
    results = collection.query(
        query_embeddings=[emb],
        n_results=N_RESULTS,
        include=["documents", "metadatas"]
    )
    foods = results["metadatas"][0]
    docs  = results["documents"][0]
    return foods, docs

# --- Build system prompt ---
SYSTEM_PROMPT = """You are NutriBot, a fast and friendly nutrition assistant.
You have access to a database of 40,000+ foods with detailed nutritional info.
Always answer using the retrieved food data provided to you.
Be concise. Use bullet points for lists. If the user asks for a meal plan, suggest specific foods from the data.
If something isn't in the retrieved data, say so honestly."""

# --- Chat endpoint (streaming) ---
@app.post("/chat")
def chat(req: ChatRequest):
    foods, docs = retrieve(req.message)

    # Build context block
    context_lines = []
    for i, (food, doc) in enumerate(zip(foods, docs), 1):
        context_lines.append(f"{i}. {doc}")
    context = "\n".join(context_lines)

    # Build messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add history (last 6 turns for speed)
    for turn in req.history[-6:]:
        messages.append(turn)

    # Inject retrieved context into user message
    augmented_user_msg = (
        f"Retrieved food data:\n{context}\n\n"
        f"User question: {req.message}"
    )
    messages.append({"role": "user", "content": augmented_user_msg})

    # Stream response
    def generate():
        stream = ollama.chat(
            model=CHAT_MODEL,
            messages=messages,
            stream=True,
            options={"temperature": 0.3, "num_predict": 512}
        )
        for chunk in stream:
            token = chunk["message"]["content"]
            yield token

    return StreamingResponse(generate(), media_type="text/plain")
