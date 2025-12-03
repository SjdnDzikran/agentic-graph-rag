import json
import os
import sys
from pathlib import Path
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from datetime import datetime
import hashlib

# Import the _env helper from settings
sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.config.settings import neo4j_uri, neo4j_username, neo4j_password, neo4j_database

NEO4J_URI = neo4j_uri
NEO4J_USER = neo4j_username
NEO4J_PASSWORD = neo4j_password
NEO4J_DB = neo4j_database

LOG_PATH = os.getenv("ATTACK_LOG_PATH", "../log/tes.jsonl")
BATCH_SIZE = 50


def parse_ts(ts: str):
    """Parse ISO timestamp, handle Z suffix."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def make_event_id(event: dict) -> str:
    """Generate deterministic event ID from timestamp + src_ip + message hash."""
    ts = event.get("timestamp", "")
    src = event.get("src_ip", "")
    msg = event.get("message", "")
    key = f"{ts}#{src}#{msg}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def ingest():
    """Delete existing LogEvent nodes and load attack log JSONL into Neo4j in batches."""
    log_file = Path(LOG_PATH)
    if not log_file.exists():
        print(f"Error: log file not found: {LOG_PATH}", file=sys.stderr)
        return

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        print(f"[neo4j] connected to {NEO4J_URI}")
    except Neo4jError as e:
        print(f"Error: failed to connect to Neo4j: {e}", file=sys.stderr)
        return

    batch = []
    total = 0
    skipped = 0

    try:
        with driver.session(database=NEO4J_DB) as session:
            # --- NEW: delete all existing LogEvent nodes first ---
            try:
                existing = session.run(
                    "MATCH (e:LogEvent) RETURN count(e) AS c"
                ).single()["c"]
                print(f"[neo4j] existing LogEvent nodes: {existing}")

                delete_result = session.run(
                    "MATCH (e:LogEvent) DETACH DELETE e"
                )
                summary = delete_result.consume()
                print(
                    f"[neo4j] deleted LogEvent nodes: "
                    f"{summary.counters.nodes_deleted}"
                )
            except Neo4jError as e:
                print(f"[error] failed to delete existing LogEvent nodes: {e}", file=sys.stderr)
                # if delete fails, better stop than mix old/new
                return

            # Now ingest fresh data from JSONL
            with open(log_file, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError as e:
                        print(f"[warn] line {line_no}: invalid JSON: {e}")
                        skipped += 1
                        continue

                    ts = parse_ts(event.get("timestamp", ""))
                    timestamp = ts.isoformat() if ts else event.get("timestamp")
                    event_id = make_event_id(event)

                    batch.append({
                        "id": event_id,
                        "timestamp": timestamp,
                        "host": event.get("host"),
                        "user": event.get("user"),
                        "src_ip": event.get("src_ip"),
                        "dst_ip": event.get("dst_ip"),
                        "program": event.get("program"),
                        "message": event.get("message"),
                        "cve": event.get("cve"),
                        "raw": json.dumps(event),
                    })

                    if len(batch) >= BATCH_SIZE:
                        _persist_batch(session, batch)
                        total += len(batch)
                        batch = []

                # flush remaining
                if batch:
                    _persist_batch(session, batch)
                    total += len(batch)

    except Exception as e:
        print(f"Error during ingestion: {e}", file=sys.stderr)
    finally:
        driver.close()
        print(f"[done] ingested {total} events, skipped {skipped}")


def _persist_batch(session, batch: list):
    """Write a batch of events in a single transaction."""
    query = """
    UNWIND $events AS evt
    MERGE (e:LogEvent {id: evt.id})
    SET e.timestamp = evt.timestamp,
        e.host = evt.host,
        e.program = evt.program,
        e.message = evt.message,
        e.src_ip = evt.src_ip,
        e.dst_ip = evt.dst_ip,
        e.raw = evt.raw

    FOREACH (_ IN CASE WHEN evt.user IS NOT NULL THEN [1] ELSE [] END |
        MERGE (u:User {id: toLower(evt.user)})
        MERGE (u)-[:TRIGGERED]->(e)
    )

    FOREACH (_ IN CASE WHEN evt.src_ip IS NOT NULL THEN [1] ELSE [] END |
        MERGE (ip:IP {addr: evt.src_ip})
        MERGE (ip)-[:SOURCE_OF]->(e)
    )

    FOREACH (_ IN CASE WHEN evt.dst_ip IS NOT NULL THEN [1] ELSE [] END |
        MERGE (ip2:IP {addr: evt.dst_ip})
        MERGE (e)-[:DESTINATION]->(ip2)
    )

    FOREACH (_ IN CASE WHEN evt.host IS NOT NULL THEN [1] ELSE [] END |
        MERGE (h:Host {name: evt.host})
        MERGE (h)-[:RECORDED]->(e)
    )

    FOREACH (_ IN CASE WHEN evt.cve IS NOT NULL THEN [1] ELSE [] END |
        MERGE (v:Vulnerability {cve: evt.cve})
        MERGE (e)-[:RELATED_TO]->(v)
    )
    """
    try:
        session.run(query, events=batch)
        print(f"[neo4j] inserted {len(batch)} events")
    except Neo4jError as e:
        print(f"[error] batch write failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    ingest()
