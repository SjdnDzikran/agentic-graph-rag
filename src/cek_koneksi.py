import os
from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase

# Load environment variables
load_dotenv(find_dotenv())

# Fallback loading
if not os.environ.get("NEO4J_AURA"):
     load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

URI = os.environ.get("NEO4J_AURA")
USERNAME = os.environ.get("NEO4J_AURA_USERNAME")
PASSWORD = os.environ.get("NEO4J_AURA_PASSWORD")

print(f"Loaded Configuration:")
print(f"URI: {URI}")
print(f"Username: {USERNAME}")
print(f"Password: {'*' * len(PASSWORD) if PASSWORD else 'None'}")

if not URI or not USERNAME or not PASSWORD:
    print("❌ ERROR: Missing Neo4j environment variables.")
    exit(1)

try:
    print(f"\nConnecting to {URI}...")
    with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
        driver.verify_connectivity()
        print("✅ SUCCESS! Connected to Neo4j.")
except Exception as e:
    print(f"❌ FAILED: {e}")