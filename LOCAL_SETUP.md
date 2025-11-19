# Local Environment Setup

Follow these steps to recreate the Agentic Graph RAG dev environment used in
this repository.

## 1. Prerequisites
- Python 3.12 (or a compatible Python 3.9+ interpreter)
- `pip` (ships with modern Python releases)

## 2. Create a Virtual Environment
```bash
python3 -m venv .venv
```

## 3. Activate the Environment
- **macOS / Linux**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (cmd.exe)**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

Your shell prompt will show `(.venv)` once the environment is active.

## 4. Install Dependencies
From the repository root (the same directory that contains `requirements.txt`)
and with the virtual environment activated:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Verify the Setup
Confirm that the core libraries installed correctly:
```bash
python - <<'PY'
import langgraph, langchain, neo4j, rdflib
from sentence_transformers import SentenceTransformer
from SPARQLWrapper import SPARQLWrapper

model = SentenceTransformer('all-MiniLM-L6-v2')
print("LangGraph version:", langgraph.__version__)
print("LangChain version:", langchain.__version__)
print("Loaded embedding model:", model.get_sentence_embedding_dimension(), "dims")
PY
```

## 6. Daily Workflow
1. Activate the environment (`source .venv/bin/activate` or Windows equivalent).
2. Work on the project.
3. When finished, exit the environment with:
   ```bash
   deactivate
   ```

> Tip: If new dependencies are added later, update `requirements.txt` with
> `pip freeze > requirements.txt` so everyone can stay in sync.
