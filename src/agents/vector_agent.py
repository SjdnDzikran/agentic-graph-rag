# src/agents/vulnerability_vector_agent.py 
from langchain_core.prompts import ChatPromptTemplate
from langchain_neo4j.vectorstores.neo4j_vector import remove_lucene_chars
from pydantic import BaseModel, Field
from typing import List, Optional
from src.config.settings import llm, graph, vector_index

# --- Entity Extraction ---
class VulnerabilityEntities(BaseModel):
    """Identifies vulnerability-related information."""

    entity_values: List[str] = Field(
        ...,
        description="All entities such as CVE IDs, Software names, Vendors, "
        "Attack vectors (e.g., Remote, Local), Vulnerability types (e.g., SQL Injection, XSS, Buffer Overflow), "
        "Products, Versions, or affected Systems that appear in the text.",
    )
    
    severity_filter: Optional[str] = Field(
        None,
        description="Severity level if mentioned: CRITICAL, HIGH, MEDIUM, LOW"
    )
    
    score_filter: Optional[float] = Field(
        None,
        description="CVSS score threshold if mentioned (0.0-10.0)"
    )

entity_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert at extracting security vulnerability information from queries. "
            "Extract CVE IDs, software names, vendors, vulnerability types, attack vectors, "
            "affected products/versions, and any severity or CVSS score filters mentioned. "
            "Examples: 'CVE-2024-1234', 'Apache', 'SQL Injection', 'Remote Code Execution', "
            "'OpenSSL 3.0', 'CRITICAL severity', 'CVSS score above 7.5'"
        ),
        (
            "human",
            "Use the given format to extract information from "
            "the following input: {question}",
        ),
    ]
)

entity_chain = entity_prompt | llm.with_structured_output(VulnerabilityEntities)

# --- Helper Functions ---
def generate_full_text_query(input: str) -> str:
    """
    Generate a full-text search query for a given input string.
    Allows for fuzzy matching (~2 changed characters per word).
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()

def structured_retriever(question: str) -> str:
    """
    Collects vulnerability information and relationships 
    mentioned in the question using entity extraction.
    """
    result = ""
    
    entities = entity_chain.invoke({"question": question})
    print(f"\n--- Extracted Entities: {entities.entity_values} ---")
    print(f"--- Severity Filter: {entities.severity_filter} ---")
    print(f"--- Score Filter: {entities.score_filter} ---")

    for entity_value in entities.entity_values:
        query = generate_full_text_query(entity_value)
        if not query:
            continue
        
        # Search for vulnerabilities and related entities
        response = graph.query(
            """
            CALL db.index.fulltext.queryNodes('vulnerability_entities', $query, {limit: 10})
            YIELD node AS entity
            
            // Find vulnerabilities related to this entity
            OPTIONAL MATCH (vuln:Vulnerability)-[:AFFECTS|:TARGETS|:EXPLOITS]-(entity)
            
            // Get additional context
            OPTIONAL MATCH (vuln)-[:AFFECTS]->(product:Product)
            OPTIONAL MATCH (vuln)-[:HAS_CWE]->(cwe:CWE)
            OPTIONAL MATCH (chunk:Chunk)-[:DESCRIBES]->(vuln)
            
            // Apply filters if specified
            WHERE ($severity IS NULL OR vuln.severity = $severity)
              AND ($min_score IS NULL OR vuln.score >= $min_score)
            
            WITH entity, vuln, product, cwe, chunk,
                 CASE 
                     WHEN 'Vulnerability' IN labels(entity) THEN entity.id
                     WHEN 'Product' IN labels(entity) THEN entity.name
                     WHEN 'Vendor' IN labels(entity) THEN entity.name
                     ELSE entity.id 
                 END AS entity_name
                 
            RETURN DISTINCT
                "Entity '" + entity_name + "' is associated with vulnerability '" + 
                coalesce(vuln.id, 'N/A') + "' (Severity: " + coalesce(vuln.severity, 'N/A') + 
                ", CVSS: " + coalesce(toString(vuln.score), 'N/A') + "). " +
                "Affects: " + coalesce(product.name, 'N/A') + ". " +
                "CWE: " + coalesce(cwe.id, 'N/A') + ". " +
                "Description: " + coalesce(left(vuln.description, 200), left(chunk.text, 200), 'N/A') + "...'"
                AS output
            LIMIT 10
            """,
            {
                "query": query,
                "severity": entities.severity_filter,
                "min_score": entities.score_filter
            },
        )
        if response:
            result += "\n".join([el['output'] for el in response])
    
    return result

# --- Main Search Function ---
def query_vector_search(question: str):
    """
    Query the graph and vector index for vulnerability information.
    Combines structured entity search with semantic vector similarity.
    """
    print(f"--- Executing Vulnerability Vector Search for: {question} ---")
    
    # Get structured data through entity extraction
    structured_data = structured_retriever(question)
    
    # Get semantically similar vulnerability descriptions
    unstructured_data = [el.page_content for el in vector_index.similarity_search(question, k=5)]
    
    final_data = f"""Structured vulnerability data:
{structured_data}

Semantically similar vulnerabilities:
{"#Vulnerability ".join(unstructured_data)}
"""
    return final_data


# --- Optional: Specialized Query Functions ---
def search_by_cve(cve_id: str):
    """Direct search for specific CVE"""
    response = graph.query(
        """
        MATCH (v:Vulnerability {id: $cve_id})
        OPTIONAL MATCH (v)-[:AFFECTS]->(p:Product)
        OPTIONAL MATCH (v)-[:HAS_CWE]->(cwe:CWE)
        RETURN v.id AS cve_id, 
               v.description AS description,
               v.score AS cvss_score,
               v.severity AS severity,
               v.published AS published,
               collect(DISTINCT p.name) AS affected_products,
               collect(DISTINCT cwe.id) AS cwe_ids
        """,
        {"cve_id": cve_id}
    )
    return response

def search_by_severity(severity: str, limit: int = 10):
    """Search vulnerabilities by severity level"""
    response = graph.query(
        """
        MATCH (v:Vulnerability {severity: $severity})
        OPTIONAL MATCH (v)-[:AFFECTS]->(p:Product)
        RETURN v.id AS cve_id,
               v.description AS description,
               v.score AS cvss_score,
               v.severity AS severity,
               collect(DISTINCT p.name) AS affected_products
        ORDER BY v.score DESC
        LIMIT $limit
        """,
        {"severity": severity.upper(), "limit": limit}
    )
    return response