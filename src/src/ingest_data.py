# src/ingest_data.py
import os
import pandas as pd
from dotenv import load_dotenv
from langchain_neo4j import Neo4jVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# 1. Load Environment Variables Manual
# (Kita load manual agar tidak trigger error dari settings.py)
load_dotenv("src/.env") 

url = os.getenv("NEO4J_AURA")
username = os.getenv("NEO4J_AURA_USERNAME")
password = os.getenv("NEO4J_AURA_PASSWORD")

print(f"Connecting to Neo4j at {url}...")

# 2. Load Embedding Model
print("Loading embedding model (all-MiniLM-L6-v2)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. Load Dataset
csv_path = r"D:\All Program\Github v2\agentic-graph-rag\data\cve_dataset.csv"
if not os.path.exists(csv_path):
    print(f"❌ Error: File {csv_path} tidak ditemukan! Pastikan Anda menjalankannya dari root folder.")
    exit()

print("Reading dataset...")
df = pd.read_csv(csv_path)

documents = []
for _, row in df.iterrows():
    # Bersihkan data NaN
    row = row.fillna("")
    
    # Format teks yang akan dijadikan vector
    content = (
        f"CVE ID: {row['id']}\n"
        f"Description: {row['description']}\n"
        f"Severity: {row['severity']}\n"
        f"Score: {row['score']}"
    )
    
    # Metadata untuk keperluan filtering nanti
    metadata = {
        "id": str(row['id']).strip(),
        "severity": str(row['severity']),
        "score": str(row['score']),
        "published": str(row['published']),
        "source": "cve_dataset.csv"
    }
    
    documents.append(Document(page_content=content, metadata=metadata))

print(f"Siap memasukkan {len(documents)} data ke Database...")

# 4. Ingest ke Neo4j (Ini yang akan membuat Index 'vector')
try:
    Neo4jVector.from_documents(
        documents,
        embeddings,
        url=url,
        username=username,
        password=password,
        index_name="vector",       # Nama index yang dicari settings.py
        keyword_index_name="keyword",
        search_type="hybrid"
    )
    print("\n✅ SUKSES! Data berhasil masuk dan Index 'vector' telah dibuat.")
    print("Sekarang file settings.py dan evaluasi Anda seharusnya bisa berjalan.")

except Exception as e:
    print(f"\n❌ Gagal melakukan ingestion: {e}")