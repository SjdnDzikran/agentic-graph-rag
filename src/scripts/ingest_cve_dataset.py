"""
Utility script to populate Neo4j with CVE documents, chunks, and indexes.

Usage:
    uv run python -m scripts.ingest_cve_dataset --csv data/cve_dataset.csv
"""

from __future__ import annotations

import argparse
import csv
import os
from itertools import islice
from pathlib import Path
from typing import Iterable, List, Sequence

from dotenv import find_dotenv, load_dotenv
from neo4j import GraphDatabase, Session
from neo4j.exceptions import Neo4jError
from sentence_transformers import SentenceTransformer

BATCH_SIZE = 50
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def chunked(iterable: Sequence[dict], size: int) -> Iterable[List[dict]]:
    """Yield fixed-size batches from a sequence."""
    iterator = iter(iterable)
    while True:
        batch = list(islice(iterator, size))
        if not batch:
            break
        yield batch


def parse_env() -> dict:
    """Load .env from repo root and return Neo4j connection details."""
    dotenv_path = find_dotenv(usecwd=True)
    if not dotenv_path:
        dotenv_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(dotenv_path)

    uri = os.environ.get("NEO4J_AURA") or os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_AURA_USERNAME") or os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_AURA_PASSWORD") or os.environ.get("NEO4J_PASSWORD_ICS")
    database = os.environ.get("NEO4J_AURA_DATABASE") or os.environ.get("NEO4J_DATABASE") or "neo4j"

    if not all([uri, user, password]):
        raise RuntimeError(
            "Missing Neo4j credentials. Ensure NEO4J_* or NEO4J_AURA_* variables "
            "are set in .env before running ingestion."
        )

    return {"uri": uri, "user": user, "password": password, "database": database}


def ensure_indexes(session: Session) -> None:
    """Create required vector and fulltext indexes if they do not exist."""
    statements = {
        "vector": """
            CREATE VECTOR INDEX vector IF NOT EXISTS
            FOR (chunk:Chunk) ON (chunk.embedding)
            OPTIONS { indexConfig: {
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
            }}
        """,
        "keyword": """
            CREATE FULLTEXT INDEX keyword IF NOT EXISTS
            FOR (chunk:Chunk) ON EACH [chunk.text]
        """,
        "entities": """
            CREATE FULLTEXT INDEX entities IF NOT EXISTS
            FOR (entity:Document) ON EACH [entity.fileName, entity.description]
        """,
    }

    for name, statement in statements.items():
        try:
            session.run(statement)
            print(f"[indexes] ensured '{name}' index")
        except Neo4jError as exc:
            # Ignore "already exists" errors to keep the script idempotent.
            if "already exists" in str(exc):
                print(f"[indexes] '{name}' already exists")
            else:
                raise


def load_rows(csv_path: Path) -> list[dict]:
    """Read the CSV file into an in-memory list of row dicts."""
    rows: list[dict] = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for record in reader:
            description = (record.get("description") or "").strip()
            if not description:
                continue
            rows.append(
                {
                    "id": record.get("id") or record.get("cve_id"),
                    "description": description,
                    "published": (record.get("published") or "").strip(),
                    "severity": (record.get("severity") or "UNKNOWN").strip(),
                    "score": record.get("score"),
                }
            )
    if not rows:
        raise RuntimeError(f"No rows containing descriptions were found in {csv_path}")
    return rows


def embed_rows(rows: list[dict]) -> list[dict]:
    """Generate embeddings for each row description."""
    model = SentenceTransformer(EMBEDDING_MODEL)
    descriptions = [row["description"] for row in rows]
    embeddings = model.encode(descriptions, convert_to_numpy=True)
    for row, embedding in zip(rows, embeddings):
        row["chunk_id"] = f"{row['id']}-chunk"
        row["embedding"] = embedding.tolist()
    return rows


def persist_rows(driver, database: str, rows: list[dict]) -> None:
    """Write documents, chunks, and relationships in batches."""
    query = """
    UNWIND $rows AS row
    MERGE (doc:Document {id: row.id})
      SET doc.fileName = row.id,
          doc.description = row.description,
          doc.published = row.published,
          doc.severity = row.severity,
          doc.score = row.score
    MERGE (chunk:Chunk {id: row.chunk_id})
      SET chunk.text = row.description,
          chunk.embedding = row.embedding,
          chunk.published = row.published,
          chunk.severity = row.severity,
          chunk.score = row.score
    MERGE (chunk)-[:PART_OF]->(doc)
    MERGE (chunk)-[:HAS_ENTITY]->(doc)
    """

    with driver.session(database=database) as session:
        for batch in chunked(rows, BATCH_SIZE):
            session.run(query, rows=batch)
            print(f"[neo4j] inserted/updated {len(batch)} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest CVE dataset into Neo4j.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "data" / "cve_dataset.csv",
        help="Path to the CVE CSV file (default: data/cve_dataset.csv)",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        raise FileNotFoundError(f"CSV file not found: {args.csv}")

    creds = parse_env()
    rows = embed_rows(load_rows(args.csv))

    driver = GraphDatabase.driver(creds["uri"], auth=(creds["user"], creds["password"]))
    try:
        with driver.session(database=creds["database"]) as session:
            ensure_indexes(session)
        persist_rows(driver, creds["database"], rows)
        print("Ingestion complete.")
    finally:
        driver.close()


if __name__ == "__main__":
    main()
