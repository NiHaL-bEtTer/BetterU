# BetterU — AI Nutrition Assistant

A local RAG-powered nutrition chatbot built with FastAPI, ChromaDB, and Ollama.
Ask questions about food, get personalized macro targets, and plan your meals — all running on your machine.

---

## Tech Stack

- **Backend** — FastAPI + Python
- **Vector DB** — ChromaDB (~48,000 foods)
- **LLM** — Ollama (phi3 recommended)
- **Embeddings** — nomic-embed-text
- **Frontend** — Vanilla HTML/CSS/JS

---

## First Time Setup (New Machine / School Laptop)

### 1. Install Python
Download from https://python.org (3.10 or higher)
During install — check **"Add Python to PATH"**

### 2. Install Ollama
Download from https://ollama.com and install it.
Then open a terminal and pull the required models:
```bash
ollama pull phi3
ollama pull nomic-embed-text
```

### 3. Clone the repo
```bash
git clone <your-github-url>
cd BetterU/Backend
```

### 4. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 5. Build the ChromaDB (required — not included in repo)
The database is not committed to GitHub. You must build it locally.

**For the main JSON dataset (foods.json):**
```bash
python injest.py
```

**To append the second CSV dataset (foods2.csv):**
```bash
python ingest_csv.py
```

> Both scripts must be run from the `Backend` folder.
> `injest.py` is the primary script — run it first.
> `ingest_csv.py` appends ~8,000 additional foods into the same collection.
> This will take several minutes — it embeds every food using nomic-embed-text.
> When finished it prints the total food count.

---

## Starting the App (Every Time)

### 1. Make sure Ollama is running
Open the Ollama app from your taskbar, or run:
```bash
ollama serve
```

### 2. Start the FastAPI server
```bash
cd C:\Users\user\Downloads\BetterU\Backend
python -m uvicorn app:app --reload
```

### 3. Open the app in your browser
```
http://127.0.0.1:8000
```

---

## Pages

| Page | URL | Description |
|------|-----|-------------|
| Chat | `http://127.0.0.1:8000` | Main NutriBot RAG chatbot |
| Profile | `http://127.0.0.1:8000/profile` | Enter stats, get TDEE + macro targets |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | RAG chatbot — streams response |
| POST | `/calculate` | Returns BMI, BMR, TDEE, macros |
| POST | `/nutribot` | Profile page LLM chat |
| GET  | `/health` | Check server status |

---

## If Something Breaks

**Restore ChromaDB from backup:**
```powershell
Remove-Item -Recurse -Force chromadb
Copy-Item -Recurse chromadb_backup chromadb
```

**Rebuild ChromaDB from scratch:**
```bash
python injest.py
python ingest_csv.py
```

**Ollama not responding:**
Make sure the Ollama app is open before starting uvicorn.

**Wrong folder error:**
Always `cd` into `Backend` before running uvicorn.

---

## Requirements

- Python 3.10+
- Ollama running locally
- Models pulled: `phi3` and `nomic-embed-text`
- `foods.json` in the Backend folder (for injest.py)
- `foods2.csv` in the Backend folder (for ingest_csv.py)
