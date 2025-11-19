from neo4j import GraphDatabase
import json

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "admin123"

def create_vector_index(driver):
    cypher = """
    CREATE VECTOR INDEX cve_vector_index IF NOT EXISTS
    FOR (v:Vulnerability)
    ON v.embedding
    OPTIONS {
      indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
      }
    }
    """
    with driver.session() as session:
        try:
            session.run(cypher)
        except Exception as e:
            print(f"Error creating index: {e}")

def upload_data(driver, json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    

    # Menggunakan SET v += properties untuk auto-handle semua field
    cypher = """
    MERGE (v:Vulnerability {id: $id})
    SET v += $properties
    """

    with driver.session() as session:
        success_count = 0
        error_count = 0
        
        for item in data:
            try:
                cve_id = item.get('id')
                # Ambil semua properties kecuali id, filter yang None
                properties = {k: v for k, v in item.items() 
                             if k != 'id' and v is not None}
                
                session.run(cypher, {'id': cve_id, 'properties': properties})
                success_count += 1
                
                if success_count % 100 == 0:
                    print(f"  Uploaded {success_count}/{len(data)} records...")
                    
            except Exception as e:
                error_count += 1

if __name__ == "__main__":
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    
    try:
        create_vector_index(driver)
        upload_data(driver, r"C:\Project\agentic-graph-rag\data\cve_with_embeddings.json")
    finally:
        driver.close()