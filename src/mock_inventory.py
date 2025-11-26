import os
from dotenv import load_dotenv, find_dotenv
from langchain_neo4j import Neo4jGraph

# Load environment variables
load_dotenv(find_dotenv())

# Initialize Neo4j Connection
neo4j_uri = os.environ.get("NEO4J_AURA", "").replace("neo4j+s://", "neo4j+ssc://")
neo4j_username = os.environ.get("NEO4J_AURA_USERNAME")
neo4j_password = os.environ.get("NEO4J_AURA_PASSWORD")

graph = Neo4jGraph(
    url=neo4j_uri,
    username=neo4j_username,
    password=neo4j_password
)

def seed_database():
    print("--- Clearing Database ---")
    graph.query("MATCH (n) DETACH DELETE n")

    print("--- Seeding Assets and Software ---")
    
    # Create Assets (Servers, Laptops, Workstations)
    graph.query("""
    CREATE (s1:Asset {id: "Server-Alpha", type: "Server", os: "Ubuntu 20.04", ip: "192.168.1.10"})
    CREATE (s2:Asset {id: "Server-Beta", type: "Server", os: "Windows Server 2019", ip: "192.168.1.11"})
    CREATE (s3:Asset {id: "Server-DB-01", type: "Server", os: "CentOS 7", ip: "192.168.1.12"})
    CREATE (l1:Asset {id: "Laptop-User01", type: "Laptop", os: "Windows 10", ip: "192.168.1.101"})
    CREATE (w1:Asset {id: "Workstation-HR-01", type: "Workstation", os: "Windows 10", ip: "192.168.1.105"})
    CREATE (w2:Asset {id: "Workstation-Dev-02", type: "Workstation", os: "Ubuntu 22.04", ip: "192.168.1.106"})
    """)

    # Create Software
    graph.query("""
    CREATE (sw1:Software {name: "Apache HTTP Server", version: "2.4.49", vendor: "Apache"})
    CREATE (sw2:Software {name: "Log4j", version: "2.14.1", vendor: "Apache"})
    CREATE (sw3:Software {name: "OpenSSL", version: "1.1.1k", vendor: "OpenSSL"})
    CREATE (sw4:Software {name: "Windows Defender", version: "4.18", vendor: "Microsoft"})
    CREATE (sw5:Software {name: "MySQL", version: "5.7", vendor: "Oracle"})
    CREATE (sw6:Software {name: "Python", version: "2.7", vendor: "Python Software Foundation"})
    CREATE (sw7:Software {name: "Adobe Reader", version: "9.0", vendor: "Adobe"})
    CREATE (sw8:Software {name: "Apache Struts", version: "2.3.31", vendor: "Apache"})
    CREATE (sw9:Software {name: "OpenSSH", version: "8.6", vendor: "OpenBSD"})
    """)

    # Create Relationships (HAS_SOFTWARE)
    
    # Server-Alpha: Apache (Vuln), Log4j (Vuln), OpenSSH (Secure)
    graph.query("""
    MATCH (a:Asset {id: "Server-Alpha"}), (s:Software)
    WHERE s.name IN ["Apache HTTP Server", "Log4j", "OpenSSH"]
    CREATE (a)-[:HAS_SOFTWARE]->(s)
    """)

    # Server-Beta: Windows Defender
    graph.query("""
    MATCH (a:Asset {id: "Server-Beta"}), (s:Software {name: "Windows Defender"})
    CREATE (a)-[:HAS_SOFTWARE]->(s)
    """)

    # Server-DB-01: MySQL 5.7 (EOL), Python 2.7 (EOL)
    graph.query("""
    MATCH (a:Asset {id: "Server-DB-01"}), (s:Software)
    WHERE s.name IN ["MySQL", "Python"]
    CREATE (a)-[:HAS_SOFTWARE]->(s)
    """)
    
    # Laptop-User01: OpenSSL
    graph.query("""
    MATCH (a:Asset {id: "Laptop-User01"}), (s:Software {name: "OpenSSL"})
    CREATE (a)-[:HAS_SOFTWARE]->(s)
    """)

    # Workstation-HR-01: Adobe Reader 9.0 (Vuln)
    graph.query("""
    MATCH (a:Asset {id: "Workstation-HR-01"}), (s:Software {name: "Adobe Reader"})
    CREATE (a)-[:HAS_SOFTWARE]->(s)
    """)

    # Workstation-Dev-02: Apache Struts (Vuln), Python 2.7 (EOL)
    graph.query("""
    MATCH (a:Asset {id: "Workstation-Dev-02"}), (s:Software)
    WHERE s.name IN ["Apache Struts", "Python"]
    CREATE (a)-[:HAS_SOFTWARE]->(s)
    """)

    print("--- Database Seeded Successfully ---")
    
    # Verify
    result = graph.query("MATCH (n) RETURN count(n) as count")
    print(f"Total Nodes: {result[0]['count']}")

if __name__ == "__main__":
    seed_database()
