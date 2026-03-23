import os
import json
import sys
import chromadb
import ollama
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH  = os.path.join(BASE_DIR, "chromadb")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "Frontend")

# Make sure calculator files are importable
sys.path.insert(0, BASE_DIR)
from calculator_tool import nutrition_calculator_tool
from nodes import (
    build_system_prompt,
    CALCULATOR_SYSTEM_PROMPT,
    needs_calculation,
)

# ── Config ────────────────────────────────────────────────────────────────

EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL  = "phi3"
N_RESULTS   = 6

# ── ChromaDB ──────────────────────────────────────────────────────────────

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection    = chroma_client.get_collection("foods")

# ── App ───────────────────────────────────────────────────────────────────

app = FastAPI(title="BetterU — Nutrition AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve frontend pages ──────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def root():
    with open(os.path.join(FRONTEND_DIR, "chat.html")) as f:
        return f.read()

@app.get("/profile", response_class=HTMLResponse)
def profile_page():
    with open(os.path.join(FRONTEND_DIR, "profile.html")) as f:
        return f.read()

# ── Schemas ───────────────────────────────────────────────────────────────



class UserProfile(BaseModel):
    age:      int   = Field(..., ge=10,  le=100)
    sex:      str   = Field(...)
    weight:   float = Field(..., ge=20,  le=300)
    height:   float = Field(..., ge=100, le=250)
    activity: str   = Field(...)
    goal:     str   = Field(...)


class ChatRequest(BaseModel):
    message: str
    history: list = []
    profile: Optional[UserProfile] = None
    calc_results: Optional[dict] = None
    user_notes: Optional[str] = None


   

class AldenRequest(BaseModel):
    message: str
    profile: Optional[UserProfile] = None

# ── RAG helpers ───────────────────────────────────────────────────────────

def embed_query(text: str):
    return ollama.embeddings(model=EMBED_MODEL, prompt=text)["embedding"]

def retrieve(query: str):
    emb     = embed_query(query)
    results = collection.query(
        query_embeddings=[emb],
        n_results=N_RESULTS,
        include=["documents", "metadatas"]
    )
    return results["metadatas"][0], results["documents"][0]

# ── /chat — RAG chatbot (chat.html) ───────────────────────────────────────

@app.post("/chat")
def chat(req: ChatRequest):
    """
    RAG-powered chat using ChromaDB food database.
    Used by chat.html — streams tokens back to the frontend.
    """
    foods, docs = retrieve(req.message)

    context = "\n".join(
        f"{i}. {doc}" for i, doc in enumerate(docs, 1)
    )

    messages = [{"role": "system", "content": build_system_prompt(req.profile, req.calc_results, req.user_notes)}]
    for turn in req.history[-6:]:
        messages.append(turn)
    messages.append({
        "role": "user",
        "content": f"Retrieved food data:\n{context}\n\nUser question: {req.message}"
    })

    def generate():
        stream = ollama.chat(
            model=CHAT_MODEL,
            messages=messages,
            stream=True,
            options={"temperature": 0.3, "num_predict": 512}
        )
        for chunk in stream:
            yield chunk["message"]["content"]

    return StreamingResponse(generate(), media_type="text/plain")

# ── /calculate — pure math, no LLM (profile.html) ────────────────────────

@app.post("/calculate")
def calculate(profile: UserProfile):
    """
    Runs calculator.py deterministically.
    No LLM involved — called by profile.html when the form is submitted.
    Returns BMI, BMR, TDEE, recommended_calories, and macros.
    """
    result = nutrition_calculator_tool({
        "age":      profile.age,
        "sex":      profile.sex,
        "weight":   profile.weight,
        "height":   profile.height,
        "activity": profile.activity,
        "goal":     profile.goal,
    })

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

# ── /alden — LLM chat using calculator results (optional client) ──────────

@app.post("/alden")
def alden(req: AldenRequest):
    """
    LLM answers using calculator results when relevant.
    The LLM explains the numbers, never computes them. Streams tokens to the client.
    """
    calc_results = None

    if needs_calculation(req.message):
        if req.profile is None:
            # No profile — ask user to fill in the form
            def ask_for_profile():
                stream = ollama.chat(
                    model=CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": CALCULATOR_SYSTEM_PROMPT},
                        {"role": "user",   "content": (
                            f'The user said: "{req.message}"\n\n'
                            "Ask them in a friendly way to fill in their profile "
                            "on the Profile page first so you can give accurate numbers."
                        )},
                    ],
                    stream=True,
                    options={"temperature": 0.3, "num_predict": 256}
                )
                for chunk in stream:
                    yield chunk["message"]["content"]
            return StreamingResponse(ask_for_profile(), media_type="text/plain")

        # Run calculator — LLM never does the math
        calc_results = nutrition_calculator_tool({
            "age":      req.profile.age,
            "sex":      req.profile.sex,
            "weight":   req.profile.weight,
            "height":   req.profile.height,
            "activity": req.profile.activity,
            "goal":     req.profile.goal,
        })

        if "error" in calc_results:
            raise HTTPException(status_code=400, detail=calc_results["error"])

        user_message = (
            f'The user said: "{req.message}"\n\n'
            f"[CALCULATOR RESULTS — use ONLY these numbers, do not recalculate]\n"
            f"{json.dumps(calc_results, indent=2)}\n\n"
            "Respond conversationally using these exact numbers. "
            "Explain what BMI, BMR, TDEE, and the macro targets mean for this person."
        )
    else:
        user_message = req.message

    def generate():
        stream = ollama.chat(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": CALCULATOR_SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            stream=True,
            options={"temperature": 0.3, "num_predict": 512}
        )
        for chunk in stream:
            yield chunk["message"]["content"]

    return StreamingResponse(generate(), media_type="text/plain")

# ── /health ───────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model": CHAT_MODEL}
