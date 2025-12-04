# src/config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.vectorstores.neo4j_vector import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

dotenv_path = find_dotenv(usecwd=True)
if not dotenv_path:
    # Fall back to the repo root (three levels up from this file).
    dotenv_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path)

# --- Environment Variables ---
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")

# Neo4j
def _env(*keys: str) -> str | None:
    """Return the first non-empty environment variable among keys."""
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return None

neo4j_uri = _env("NEO4J_AURA", "NEO4J_URI")
neo4j_username = _env("NEO4J_AURA_USERNAME", "NEO4J_USERNAME")
neo4j_password = _env("NEO4J_AURA_PASSWORD", "NEO4J_PASSWORD_ICS")
neo4j_database = _env("NEO4J_AURA_DATABASE", "NEO4J_DATABASE")

if not all([neo4j_uri, neo4j_username, neo4j_password]):
    raise ValueError(
        "Neo4j connection details are missing. Please set NEO4J_AURA_* or "
        "NEO4J_* variables in your .env file."
    )

# Langchain
os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_ENDPOINT"] = os.environ.get("LANGCHAIN_ENDPOINT", "")

# --- LLM init ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-09-2025",
    temperature=0,
    # ensure responses are concise/deterministic for downstream chains
    convert_system_message_to_human=True,
)

# Koneksi ke DB Lokal (MITRE ATT&CK)
graph = Neo4jGraph(
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password,
    database=neo4j_database,
)

# --- Global Configs & Schema ---
DEFAULT_MAX_ITERATIONS = 3
NEO4J_SCHEMA_RAW = graph.schema
NEO4J_SCHEMA_ESCAPED_FOR_PROMPT = NEO4J_SCHEMA_RAW.replace("{", "{{").replace("}", "}}")


VECTOR_INDEX_NAME = "vector"
KEYWORD_INDEX_NAME = "keyword"

# --- Embeddings Model ---
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# --- Vector Index Init ---
vector_index = Neo4jVector.from_existing_index(
    embedding=embeddings,
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password,
    database=neo4j_database,
    index_name=VECTOR_INDEX_NAME,
    keyword_index_name=KEYWORD_INDEX_NAME,
    search_type="hybrid"
)
