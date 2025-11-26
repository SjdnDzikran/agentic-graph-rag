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
        5. For property searches, use case-insensitive matching. E.g., to search for a Asset, use `toLower(a.id) CONTAINS 'search_term'`.
        6. Assign a meaningful alias to every node and relationship in the MATCH clause (e.g., `MATCH (a:Asset)-[r:HAS_SOFTWARE]->(s:Software)`).
        7. In the RETURN clause, include only the components (nodes, relationships, or properties) needed to answer the question.
        8. To count distinct items from an `OPTIONAL MATCH`, collect them first and then use `size()` on the list to avoid null value warnings.
        9. To create unique pairs of nodes for comparison, use `WHERE elementId(node1) < elementId(node2)`.
        10. **CRITICAL RULE**: When returning the `type()` of a relationship, you MUST give the relationship a variable in the `MATCH` clause.

Schema:
{schema}

Note: 
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than for you to construct a Cypher statement.
Do not run any queries that would add to or delete from the database.

Examples:

1.  Question: What software is installed on Server-Alpha?
    Query:
    MATCH (a:Asset)-[:HAS_SOFTWARE]->(s:Software)
    WHERE toLower(a.id) = 'server-alpha'
    RETURN a.id AS Asset, s.name AS Software, s.version AS Version

2.  Question: Which assets have Log4j installed?
    Query:
    MATCH (a:Asset)-[:HAS_SOFTWARE]->(s:Software)
    WHERE toLower(s.name) CONTAINS 'log4j'
    RETURN a.id AS Asset, a.ip AS IP, s.version AS Version

3.  Question: List all servers running Windows.
    Query:
    MATCH (a:Asset)
    WHERE toLower(a.os) CONTAINS 'windows' AND a.type = 'Server'
    RETURN a.id AS Asset, a.ip AS IP, a.os AS OS

4.  Question: Count how many software packages are on each asset.
    Query:
    MATCH (a:Asset)-[:HAS_SOFTWARE]->(s:Software)
    RETURN a.id AS Asset, count(s) AS SoftwareCount
    ORDER BY SoftwareCount DESC

The question is:
{question}
"""

cyper_generation_prompt = PromptTemplate(
    template=cypher_generation_template,
    input_variables=["schema","question"]
)

# --- Cypher QA Prompt Template ---
qa_template = """
You are an assistant that takes the results from a Neo4j Cypher query and forms a human-readable response. The query results section contains the results of a Cypher query that was generated based on a user's natural language question. The provided information is authoritative; you must never question it or use your internal knowledge to alter it. Make the answer sound like a response to the question.
Final answer should be easily readable and structured.
Query Results:
{context}

Question: {question}
If the provided information is empty, respond by stating that you don't know the answer. Empty information is indicated by: []
If the information is not empty, you must provide an answer using the results. If the question involves a time duration, assume the query results are in units of days unless specified otherwise.
Never state that you lack sufficient information if data is present in the query results. Always utilize the data provided.
Helpful Answer:
"""

qa_generation_prompt = PromptTemplate(
    template=qa_template,
    input_variables=["context", "question"]
)

# --- Cypher QA Chain and Query Function ---
# --- Cypher QA Chain and Query Function ---
cypher_qa_chain = GraphCypherQAChain.from_llm(
    top_k=10,
    graph=graph,
    verbose=True,
    validate_cypher=True,
    return_intermediate_steps=True,
    cypher_prompt=cyper_generation_prompt,
    qa_prompt=qa_generation_prompt,
    qa_llm=ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0),
    cypher_llm=ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0),
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