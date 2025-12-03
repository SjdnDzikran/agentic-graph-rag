# src/agents/cypher_agent.py
from langchain_core.prompts import PromptTemplate
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import graph

# --- Cypher Generation Prompt Template ---
cypher_generation_template = """
You are an expert Neo4j Cypher translator who converts English questions into Cypher queries
using ONLY the Neo4j schema provided below.

GENERAL RULES:
1. Generate Cypher queries compatible ONLY with Neo4j Version 5.
2. Do NOT use: EXISTS, SIZE, HAVING. When using WITH, always use aliases.
3. Use ONLY node labels, relationship types, and properties that are present in the schema text below.
   - Do NOT invent labels, relationship types, or properties that are not explicitly shown.
4. Do NOT write any query that creates, updates, or deletes data.
   - NO: CREATE, MERGE new nodes for side effects, DELETE, SET for updates.
   - You may use MERGE only for matching patterns that already exist if clearly needed, but PREFER MATCH.
5. Always assign a meaningful alias to each node and relationship in MATCH, e.g.:
   - MATCH (u:User)-[r:TRIGGERED]->(e:LogEvent)
6. In the RETURN clause, include ONLY what is necessary to answer the question
   (specific properties, nodes, or relationships).
7. For property searches (e.g. search by user name, IP, message text), use case-insensitive matching:
   - Use `toLower(<property>) CONTAINS 'search_term'`.
   - Choose the most relevant string property based on the schema (e.g. id, name, username, message, raw, addr).
8. When searching text such as "reverse shell", "failed login", or "SQL injection",
   prefer text-like properties (from the schema) such as `message`, `raw`, `description`, `name`, etc.
9. When the question mentions a “user”, “account”, or “actor”, prefer nodes that look like users
   (e.g. :User or any label with user-like properties in the schema), and search their identifying string properties.
10. When the question mentions an IP address, use nodes/fields from the schema that represent IPs
    (e.g. :IP with property addr, or any other label/property that clearly stores IPs).
11. When the question mentions a host, server, or machine, use host/server-like labels from the schema (e.g. :Host)
    and their key properties (e.g. name, id).
12. When the question mentions vulnerabilities, CVEs, or CVSS, use vulnerability-like labels (e.g. :Vulnerability)
    and properties such as cve, id, score, etc. ONLY if they appear in the schema.
13. To count distinct items from an OPTIONAL MATCH, collect first, then use size() on the collection:
    - WITH main, collect(DISTINCT opt) AS items
      RETURN size(items) AS itemCount
14. To create unique pairs of nodes, use `WHERE elementId(a) < elementId(b)`.
15. CRITICAL: When returning `type()` of a relationship, always bind it to a variable in MATCH:
    - GOOD:  MATCH (u:User)-[r:HAS_SESSION]->(s:Server) RETURN type(r)
    - NEVER: RETURN type(:HAS_SESSION)

SCHEMA (this is the ONLY source of truth about labels, relationships, and properties):
{schema}

IMPORTANT:
- Respond with ONLY a valid Cypher query (no explanations, no comments, no backticks).
- If the question cannot be answered with the given schema, still return a syntactically valid query that best approximates the intent using only the schema.

EXAMPLES (adapted to whatever labels/props actually exist in the schema):

1. Question: Which users have generated the most events?
   Query:
   MATCH (u:User)-[r]->(e)
   RETURN u.id AS userId, count(e) AS eventCount
   ORDER BY eventCount DESC
   LIMIT 10

2. Question: Show all activity for user 'dzikran' in time order.
   Query:
   MATCH (u:User)-[r]->(n)
   WHERE toLower(u.id) CONTAINS 'dzikran'
   RETURN u.id AS user, type(r) AS relationship, labels(n) AS nodeLabels, n
   ORDER BY n.timestamp ASC

3. Question: Find log events that look like reverse shell activity.
   Query:
   MATCH (e)
   WHERE exists(e.message)
     AND (
       toLower(e.message) CONTAINS 'reverse shell'
       OR toLower(e.message) CONTAINS 'bash -i'
       OR toLower(e.message) CONTAINS 'connect back'
     )
   RETURN e
   ORDER BY e.timestamp ASC

4. Question: List all events involving CVEs and how many events per CVE.
   Query:
   MATCH (e)-[r]->(v:Vulnerability)
   WHERE exists(v.cve)
   RETURN v.cve AS cve, count(e) AS eventCount
   ORDER BY eventCount DESC

5. Question: For source IP '203.0.113.55', list related events with timestamps and messages.
   Query:
   MATCH (ip)-[r]->(e)
   WHERE exists(ip.addr) AND ip.addr = '203.0.113.55'
   RETURN e.timestamp AS timestamp, e, ip.addr AS srcIp
   ORDER BY e.timestamp ASC

The question is:
{question}
"""

cyper_generation_prompt = PromptTemplate(
    template=cypher_generation_template,
    input_variables=["schema", "question"],
)

# --- Cypher QA Prompt Template ---
qa_template = """
You are an assistant that takes the results from a Neo4j Cypher query and forms a human-readable response.
The query results section contains the results of a Cypher query that was generated based on a user's natural language question.
The provided information is authoritative; you must never question it or use your internal knowledge to alter it.
Make the answer sound like a response to the question.
Final answer should be easily readable and structured.

Query Results:
{context}

Question: {question}

If the provided information is empty, respond by stating that you don't know the answer. Empty information is indicated by: [].
If the information is not empty, you must provide an answer using the results.
If the question involves a time duration, assume the query results are in units of days unless specified otherwise.
Never state that you lack sufficient information if data is present in the query results. Always utilize the data provided.

Helpful Answer:
"""

qa_generation_prompt = PromptTemplate(
    template=qa_template,
    input_variables=["context", "question"],
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
    use_function_response=True,
)

def query_cypher(question: str) -> dict:
    """
    Generate and run a Cypher query against the graph database.
    Use this for complex questions requiring structured data, aggregations,
    or specific graph traversals.
    Returns the generated query and the result context.
    """
    print(f"--- Executing Cypher Search for: {question} ---")
    response = cypher_qa_chain.invoke({"query": question})
    return {
        "query": response["intermediate_steps"][0]["query"],
        "context": response["intermediate_steps"][1]["context"],
    }
