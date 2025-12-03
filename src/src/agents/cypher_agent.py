# src/agents/cypher_agent.py
from langchain_core.prompts import PromptTemplate
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import graph

# --- Cypher Generation Prompt Template ---
cypher_generation_template = """
You are an expert Neo4j Cypher translator who converts English to Cypher based on the Neo4j Schema provided, following the instructions below:
        1. Generate Cypher query compatible ONLY for Neo4j Version 5.
        2. Do not use EXISTS, SIZE, HAVING keywords in the cypher. Use an alias when using the WITH keyword.
        3. Use only Node labels and Relationship types mentioned in the schema.
        4. Do not use relationships that are not mentioned in the given schema.
        5. For property searches, use case-insensitive matching. E.g., to search for a CVE, use `toLower(cve.id) CONTAINS 'search_term'`.
        6. Assign a meaningful alias to every node and relationship in the MATCH clause (e.g., `MATCH (cve:CVE)-[r:EXPLOITS]->(cwe:CWE)`).
        7. In the RETURN clause, include only the components (nodes, relationships, or properties) needed to answer the question.
        8. To count distinct items from an `OPTIONAL MATCH`, collect them first and then use `size()` on the list to avoid null value warnings (e.g., `WITH main, collect(DISTINCT opt) AS items RETURN size(items) AS itemCount`).
        9. To create unique pairs of nodes for comparison, use `WHERE elementId(node1) < elementId(node2)`.
        10. **CRITICAL RULE**: When returning the `type()` of a relationship, you MUST give the relationship a variable in the `MATCH` clause. E.g., `MATCH (cve:CVE)-[r:HAS_CWE]->(cwe:CWE) RETURN type(r)`. Do NOT use `type()` on a relationship without a variable.

Schema:
{schema}

Note: 
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than for you to construct a Cypher statement.
Do not run any queries that would add to or delete from the database.

Examples:

1.  Question: Which vulnerabilities have the highest CVSS scores?
    Query:
    MATCH (cve:CVE)
    WHERE cve.cvss_score IS NOT NULL
    RETURN cve.id AS cveId, cve.cvss_score AS cvssScore, cve.description AS description
    ORDER BY cvssScore DESC
    LIMIT 10

2.  Question: List all attack patterns (CAPEC) associated with a specific weakness type.
    Query:
    MATCH (cwe:CWE)-[r:HAS_CAPEC|RELATED_TO]->(capec:CAPEC)
    RETURN cwe.id AS cweId, cwe.name AS weaknessName, type(r) AS relationship, capec.id AS capecId, capec.name AS attackPattern
    LIMIT 20

3.  Question: Show the full vulnerability chain from CVE to CWE to CAPEC for critical vulnerabilities
    Query:
    MATCH (cve:CVE)-[r1:HAS_CWE]->(cwe:CWE)-[r2:HAS_CAPEC]->(capec:CAPEC)
    WHERE cve.cvss_score >= 9.0
    RETURN
        cve.id AS cveId,
        cve.cvss_score AS cvssScore,
        type(r1) AS cveToWeakness,
        cwe.id AS cweId,
        cwe.name AS weaknessName,
        type(r2) AS weaknessToAttack,
        capec.id AS capecId,
        capec.name AS attackPattern
    LIMIT 15
        
4.  Question: Give me information about CVE-2024-1234 vulnerability?
    Query:
    MATCH (cve:CVE)-[r]->(n)
    WHERE toLower(cve.id) = 'cve-2024-1234'
    RETURN cve.id AS vulnerability, type(r) as relationship, labels(n) AS relatedEntityType, n.id as entityId, n.name as entityName

5.  Question: Which products or vendors are affected by the most critical vulnerabilities?
    Query:
    MATCH (cve:CVE)-[r:AFFECTS]->(product)
    WHERE cve.cvss_score >= 7.0
    RETURN labels(product) AS productType, product.name AS productName, count(cve) AS vulnerabilityCount, avg(cve.cvss_score) AS avgCVSS
    ORDER BY vulnerabilityCount DESC
    LIMIT 10

6.  Question: Find mitigation strategies for a specific CWE weakness
    Query:
    MATCH (cwe:CWE)-[r:HAS_MITIGATION]->(mitigation)
    WHERE toLower(cwe.id) CONTAINS 'cwe-79'
    RETURN cwe.id AS weaknessId, cwe.name AS weaknessName, mitigation.technique AS mitigationTechnique, mitigation.description AS mitigationDescription

7.  Question: What are the most exploitable vulnerabilities based on exploit availability?
    Query:
    MATCH (cve:CVE)-[r:HAS_EXPLOIT]->(exploit)
    RETURN cve.id AS cveId, cve.cvss_score AS cvssScore, cve.exploitability_score AS exploitability, count(exploit) AS exploitCount
    ORDER BY exploitability DESC, exploitCount DESC
    LIMIT 10

The question is:
{question}
"""

cyper_generation_prompt = PromptTemplate(
    template=cypher_generation_template,
    input_variables=["schema","question"]
)

# --- Cypher QA Prompt Template ---
qa_template = """
You are a vulnerability assessment assistant that takes the results from a Neo4j Cypher query and forms a human-readable response. The query results section contains the results of a Cypher query that was generated based on a user's natural language question. The provided information is authoritative; you must never question it or use your internal knowledge to alter it. Make the answer sound like a response to the question.
Final answer should be easily readable and structured.

Query Results:
{context}

Question: {question}

If the provided information is empty, respond by stating that you don't know the answer. Empty information is indicated by: []
If the information is not empty, you must provide an answer using the results. If the question involves vulnerability scores, interpret CVSS scores as: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.1-3.9).
When discussing vulnerabilities, include relevant mitigation advice from CWE/CAPEC data when available.
Never state that you lack sufficient information if data is present in the query results. Always utilize the data provided.

Helpful Answer:
"""

qa_generation_prompt = PromptTemplate(
    template=qa_template,
    input_variables=["context", "question"]
)

# --- Cypher QA Chain and Query Function ---
gemini_kwargs = {
    "model": "gemini-2.5-flash",
    "temperature": 0,
    "convert_system_message_to_human": True,
}

cypher_qa_chain = GraphCypherQAChain.from_llm(
    top_k=10,
    graph=graph,
    verbose=True,
    validate_cypher=True,
    return_intermediate_steps=True,
    cypher_prompt=cyper_generation_prompt,
    qa_prompt=qa_generation_prompt,
    qa_llm=ChatGoogleGenerativeAI(**gemini_kwargs),
    cypher_llm=ChatGoogleGenerativeAI(**gemini_kwargs),
    allow_dangerous_requests=True,
    use_function_response=True
)

def query_cypher(question: str) -> dict:
    """
    Generate and run a Cypher query against the graph database.
    Use this for complex questions requiring structured data, aggregations, or specific graph traversals
    Returns the query and the result context.
    """
    print(f"--- Executing Cypher Search for: {question} ---")
    response = cypher_qa_chain.invoke({"query": question})
    return {
        "query": response["intermediate_steps"][0]["query"],
        "context": response["intermediate_steps"][1]["context"]
    }
