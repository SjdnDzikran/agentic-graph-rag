# src/agents/vector_agent.py 
from langchain_core.prompts import ChatPromptTemplate
from langchain_neo4j.vectorstores.neo4j_vector import remove_lucene_chars
from pydantic import BaseModel, Field
from typing import List
from src.config.settings import llm, graph, vector_index

# --- Entity Extraction ---
class LogEntities(BaseModel):
    """Identifies information about vulnerability-related resources."""

    entity_values: List[str] = Field(
        ...,
        description="All entities such as CVE IDs, CWE IDs, CAPEC IDs, "
        "Product names, Vendor names, Software versions, Component names, "
        "CVSS scores, Exploit names, or Mitigation techniques that appear in the text.",
    )

entity_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert at extracting vulnerability-related entities from text. "
            "Extract CVE identifiers (e.g., CVE-2024-1234), CWE identifiers (e.g., CWE-79), "
            "CAPEC identifiers (e.g., CAPEC-18), product names, vendor names, software versions, "
            "affected components, CVSS scores, exploit names, and mitigation techniques.",
        ),
        (
            "human",
            "Use the given format to extract information from "
            "the following input: {question}",
        ),
    ]
)

entity_chain = entity_prompt | llm.with_structured_output(LogEntities)

# --- Helper Functions ---
def generate_full_text_query(input: str) -> str:
    """
    Generate a full-text search query for a given input string.

    This function constructs a query string suitable for a full-text search.
    It processes the input string by splitting it into words and appending a
    similarity threshold (~2 changed characters) to each word, then combines
    them using the AND operator. Useful for mapping entities from user questions
    to database values, and allows for some misspelings.
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(input).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()

def structured_retriever(question: str) -> str:
    """
    Collects the neighborhood of resources mentioned
    in the question
    """
    result = ""
    
    entities = entity_chain.invoke({"question": question})
    print(f"\n--- Extracted Entities: {entities.entity_values} ---")

    for entity_value in entities.entity_values:
        query = generate_full_text_query(entity_value)
        if not query:
            continue
        
        response = graph.query(
            """
            CALL db.index.fulltext.queryNodes('entities', $query, {limit: 10})
            YIELD node AS entity
            
            MATCH (chunk:Chunk)-[:HAS_ENTITY]->(entity)
            
            OPTIONAL MATCH (chunk)-[:PART_OF]->(doc:VulnerabilityReport)
            
            WITH entity, chunk, doc,
                 CASE WHEN 'CVE' IN labels(entity) 
                      THEN entity.id 
                      WHEN 'CWE' IN labels(entity)
                      THEN entity.id
                      WHEN 'CAPEC' IN labels(entity)
                      THEN entity.id
                      WHEN 'Product' IN labels(entity)
                      THEN entity.name
                      ELSE entity.id 
                 END AS entity_name
                 
            RETURN "Entity '" + entity_name + "' found in vulnerability report '" + coalesce(doc.reportId, 'N/A') +
                   "'. Context: '" + left(chunk.text, 250) + "...'"
                   AS output
            LIMIT 10
            """,
            {"query": query},
        )
        if response:
            result += "\n".join([el['output'] for el in response])
    return result

# --- Main Search Function ---
def query_vector_search(question: str):
    """
    Query the graph and vector index using a vector approach for vector similarity search.
    This is for questions that require finding similar concepts or descriptions.
    """
    print(f"--- Executing Vector Search for: {question} ---")
    structured_data = structured_retriever(question)
    unstructured_data = [el.page_content for el in vector_index.similarity_search(question)]
    final_data = f"""Structured data:
    {structured_data}
    Unstructured data:
    {"#Resource ". join(unstructured_data)}
    """
    return final_data