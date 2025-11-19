# src/config/settings.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.vectorstores.neo4j_vector import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# --- Environment Variables ---
if not os.environ.get("OPENROUTER_API_KEY"):
    raise ValueError("OPENROUTER_API_KEY tidak ditemukan di file .env!")

# --- LLM Init (OpenRouter) ---
llm = ChatOpenAI(
    model="z-ai/glm-4.5-air:free",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)

# --- Neo4j Connection ---
neo4j_uri = os.environ.get("NEO4J_AURA")
neo4j_username = os.environ.get("NEO4J_AURA_USERNAME")
neo4j_password = os.environ.get("NEO4J_AURA_PASSWORD")

graph = Neo4jGraph(
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password
)

# --- MISSING PART (Ini yang menyebabkan Error) ---
# Tambahkan bagian ini agar bisa di-import oleh file lain
NEO4J_SCHEMA_RAW = graph.schema
NEO4J_SCHEMA_ESCAPED_FOR_PROMPT = NEO4J_SCHEMA_RAW.replace("{", "{{").replace("}", "}}")
DEFAULT_MAX_ITERATIONS = 3
# ------------------------------------------------

# --- Embeddings & Vector Index ---
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

VECTOR_INDEX_NAME = "vector"
KEYWORD_INDEX_NAME = "keyword"

vector_index = Neo4jVector.from_existing_index(
    embedding=embeddings,
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password,
    index_name=VECTOR_INDEX_NAME,
    keyword_index_name=KEYWORD_INDEX_NAME,
    search_type="hybrid"
)