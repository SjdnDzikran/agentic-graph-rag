from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class GuardrailsRouterOutput(BaseModel):
    """
    Combined output for guardrails checking and routing decisions
    """
    decision: Literal["relevant", "irrelevant"] = Field(
        description="Checks if the question is relevant to vulnerability assessment topics including CVE analysis, CVSS scoring, exploitability evaluation, weakness identification (CWE), attack patterns (CAPEC), and mitigation strategies."
    )
    datasource: Literal["vulnerability_analysis", "weakness_knowledge"] = Field(
        description="Routes relevant questions to 'vulnerability_analysis' for specific CVE queries, CVSS scoring, exploitability analysis, and affected products, or to 'weakness_knowledge' for CWE weaknesses, CAPEC attack patterns, and mitigation strategies. Only populated if decision is 'relevant'."
    )

guardrails_router_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """
        You are a gatekeeper and router for a Q&A system that queries a vulnerability assessment knowledge graph.
        Your task is to:
        1. Determine if a question is answerable by the graph (guardrails)
        2. If relevant, route it to the appropriate tool
        
        The graph contains two types of information:
            1. **Vulnerability Data:** Detailed records of CVE vulnerabilities, including CVSS scores, exploitability metrics, affected products, vendors, and exploit availability.
            2. **Weakness & Attack Knowledge:** Knowledge base containing CWE (Common Weakness Enumeration), CAPEC (Common Attack Pattern Enumeration), mitigation strategies, and threat intelligence.

        **GUARDRAILS RULES:**
        - A question is **relevant** if it asks about vulnerability assessment, CVE analysis, weakness identification, attack patterns, CVSS scoring, exploitability, mitigation strategies, OR security risk evaluation.
        - A question is **irrelevant** if it is completely off-topic (e.g., 'what is the weather?', 'tell me a joke').

        **ROUTING RULES (only apply if question is relevant):**
        1. **Prioritize Vulnerability Analysis**: If the question is about specific CVEs, vulnerability scoring, exploitability, affected products, or vulnerability ranking, route it to 'vulnerability_analysis'.
        2. **Use Weakness Knowledge for General Queries**: If the question is about CWE weaknesses, CAPEC attack patterns, mitigation strategies, or general security knowledge, route it to 'weakness_knowledge'.

        Only allow relevant questions to pass with appropriate routing.
        """
    ),
    ("human", "Question: {question}"),
])

guardrails_router_chain = guardrails_router_prompt | llm.with_structured_output(GuardrailsRouterOutput)