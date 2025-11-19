from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer

class CVEVectorAgent:
    def __init__(self, uri, user, pwd, index_name="cve_vector_index"):
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))
        self.index = index_name
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text):
        """Convert text to embedding vector"""
        return self.model.encode(text).tolist()

    def search(self, text, k=5):
        """Search for similar CVEs using vector similarity"""
        vector = self.embed(text)

        query = f"""
        CALL db.index.vector.queryNodes('{self.index}', $k, $vector)
        YIELD node, score
        RETURN 
            node.id AS cve_id,
            node.description AS description,
            node.score AS cvss_score,
            node.severity AS severity,
            node.published AS published,
            score AS similarity_score
        ORDER BY score DESC
        """

        with self.driver.session() as session:
            try:
                results = session.run(query, vector=vector, k=k).data()
                return results
            except Exception as e:
                print(f"Error during search: {e}")
                return []

    def search_with_filter(self, text, k=5, min_score=None, severity=None):
        """Search with additional filters"""
        vector = self.embed(text)

        query = f"""
        CALL db.index.vector.queryNodes('{self.index}', $k, $vector)
        YIELD node, score
        WHERE ($min_score IS NULL OR node.score >= $min_score)
          AND ($severity IS NULL OR node.severity = $severity)
        RETURN 
            node.id AS cve_id,
            node.description AS description,
            node.score AS cvss_score,
            node.severity AS severity,
            node.published AS published,
            score AS similarity_score
        ORDER BY score DESC
        """

        with self.driver.session() as session:
            try:
                results = session.run(
                    query, 
                    vector=vector, 
                    k=k*2,  # Fetch more to account for filtering
                    min_score=min_score,
                    severity=severity
                ).data()
                return results[:k]  # Return top k after filtering
            except Exception as e:
                print(f"Error during filtered search: {e}")
                return []

    def get_cve_details(self, cve_id):
        """Get full details of a specific CVE"""
        query = """
        MATCH (v:Vulnerability {id: $cve_id})
        RETURN 
            v.id AS cve_id,
            v.description AS description,
            v.score AS cvss_score,
            v.severity AS severity,
            v.published AS published
        """
        
        with self.driver.session() as session:
            result = session.run(query, cve_id=cve_id).single()
            return dict(result) if result else None

    def close(self):
        """Close database connection"""
        self.driver.close()
        print("Connection closed")


def print_results(results):
    """Pretty print search results"""
    if not results:
        print("No results found")
        return
    
    print(f"\n{'='*80}")
    print(f"Found {len(results)} results:")
    print(f"{'='*80}\n")
    
    for i, result in enumerate(results, 1):
        print(f"#{i} {result['cve_id']} (Similarity: {result['similarity_score']:.4f})")
        print(f"   CVSS Score: {result.get('cvss_score', 'N/A')}")
        print(f"   Severity: {result.get('severity', 'N/A')}")
        print(f"   Published: {result.get('published', 'N/A')}")
        print(f"   Description: {result['description'][:150]}...")
        print()


if __name__ == "__main__":
    # Initialize agent
    agent = CVEVectorAgent("bolt://localhost:7687", "neo4j", "admin123")
    
    try:
        # Example 1: Basic search
        print("\nSearching for: 'SSL vulnerability'")
        results = agent.search("SSL vulnerability", k=5)
        print_results(results)
        
        # Example 2: Search with filter
        print("\n🔍 Searching for: 'remote code execution' (High severity only)")
        results = agent.search_with_filter(
            "remote code execution", 
            k=5, 
            severity="HIGH"
        )
        print_results(results)
        
        # Example 3: Get specific CVE details
        if results:
            cve_id = results[0]['cve_id']
            print(f"\n Details for {cve_id}:")
            details = agent.get_cve_details(cve_id)
            if details:
                for key, value in details.items():
                    print(f"   {key}: {value}")
    
    finally:
        agent.close()