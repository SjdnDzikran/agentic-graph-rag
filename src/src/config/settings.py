# src/config/settings.py
import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.vectorstores.neo4j_vector import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv(find_dotenv())

# Fallback: try to load from parent directory if not found
if not os.environ.get("GOOGLE_API_KEY"):
    load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

# --- Environment Variables ---
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")

# Neo4j
# Automatically use ssc (skip self signed cert) if +s is provided, to fix SSL errors
neo4j_uri = os.environ.get("NEO4J_AURA", "").replace("neo4j+s://", "neo4j+ssc://")
neo4j_username = os.environ.get("NEO4J_AURA_USERNAME")
neo4j_password = os.environ.get("NEO4J_AURA_PASSWORD")

# Langchain
os.environ["LANGCHAIN_TRACING_V2"] = os.environ.get("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.environ.get("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_API_KEY"] = os.environ.get("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_ENDPOINT"] = os.environ.get("LANGCHAIN_ENDPOINT", "")

# --- LLM init ---
# Using Google Gemini Flash Latest (generic alias)
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    temperature=0,
    max_retries=2,
)

# Koneksi ke DB Lokal (MITRE ATT&CK)
graph = Neo4jGraph(
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password
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
    index_name=VECTOR_INDEX_NAME,
    keyword_index_name=KEYWORD_INDEX_NAME,
    search_type="hybrid"
)