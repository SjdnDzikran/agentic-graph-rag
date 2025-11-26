# ### src/agents/reflection_agents.py ###
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm, NEO4J_SCHEMA_ESCAPED_FOR_PROMPT

class RephrasedQuestion(BaseModel):
    rephrased_question: str = Field(description="A rephrased, more specific version of the original question to improve answer generation.")

# --- Vector Reflection ---
vector_reflection_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a vulnerability query correction expert. A vector search returned insufficient or irrelevant vulnerability context.
        Your task is to rephrase the user's question to be more specific and likely to succeed with a vector/keyword search in the vulnerability database.
        Analyze the original question and the insufficient context. For example:
        - If the question was too broad (e.g., "tell me about vulnerabilities"), suggest adding specific CVE IDs, CVSS score ranges, or product names.
        - If it used ambiguous terms, make them clearer (e.g., "critical bugs" → "CVEs with CVSS score >= 9.0").
        - If searching for weaknesses, include CWE identifiers or specific weakness categories.
        - If searching for mitigations, specify the vulnerability type or attack pattern (CAPEC).
        Do not just repeat the question. Provide a meaningful improvement focused on vulnerability assessment terminology.
        """
    ),
    (
        "human",
        "Original Question: {original_question}\n\nInsufficient Context from Vector Search:\n{vulnerability_vector_context}\n\nRephrase the question to improve the chances of getting a better result."
    ),
])
vector_reflection_chain = vector_reflection_prompt | llm.with_structured_output(RephrasedQuestion)
# --- Cypher Reflection ---
cypher_reflection_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        f"""
        You are a vulnerability query correction expert. A Cypher query returned no results from the vulnerability knowledge graph.
        Your task is to rephrase the user's question to be more specific and likely to succeed with the given Neo4j vulnerability schema.
        Analyze the failed query and the schema. For example:
        - If the question was too broad (e.g., "find vulnerabilities"), specify criteria like CVSS score ranges, specific CVE IDs, or affected products.
        - If it used terms not in the schema (e.g., "bugs" instead of "CVE", "flaws" instead of "CWE"), suggest the correct node labels and properties.
        - If searching for relationships, ensure they exist in the schema (e.g., HAS_CWE, HAS_CAPEC, AFFECTS, HAS_MITIGATION).
        - If filtering failed, suggest using properties that exist (e.g., cvss_score, exploitability_score, severity).
        Do not just repeat the question. Provide a meaningful improvement using vulnerability assessment terminology aligned with the schema.
        
        Schema:
        {NEO4J_SCHEMA_ESCAPED_FOR_PROMPT}
        """
    ),
    (
        "human", 
        "Original Question: {original_question}\n\nFailed Cypher Query:\n{cypher_query}\n\nRephrase the question to improve the chances of getting a result from the vulnerability knowledge graph."
    ),
])
reflection_chain = cypher_reflection_prompt | llm.with_structured_output(RephrasedQuestion)