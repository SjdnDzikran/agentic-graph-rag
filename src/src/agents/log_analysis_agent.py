from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class LogAnalysisOutput(BaseModel):
    """
    Output model for the vulnerability analysis agent
    """
    decision: Literal["weakness_kb_required", "weakness_kb_not_required"] = Field(
        description="Checks if deeper analysis with weakness and attack pattern knowledge base (CWE/CAPEC) is required for mitigation strategies or attack context"
    )
    vulnerability_summary: str = Field(
        description="A concise summary of the findings from the vulnerability data (CVE, CVSS scores, exploitability, affected products) that answers the original question."
    )
    generated_question: str = Field(
        description="Question for the weakness knowledge base (CWE/CAPEC) based on original user's question and provided vulnerability context (CVE findings) to retrieve mitigation strategies or attack patterns."
    )

log_analysis_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """You are a vulnerability assessment expert. You have received structured and unstructured data from vulnerability databases.
        Your tasks are:
        1.  Summarize the findings from the provided vulnerability context to directly answer the user's original question.
        2.  Based on the user's original question, determine whether it requires further analysis with weakness and attack pattern knowledge base (CWE/CAPEC). 
        3.  Return 'weakness_kb_required' if the user's original question requires further analysis with CWE/CAPEC knowledge base for mitigation strategies or attack patterns. Return 'weakness_kb_not_required' if it does not. 

        """
    ),
    (
        "human", 
        """
        Original Question: {original_question}

        Context from Vector Search:
        {vulnerability_vector_context}

        Context from Cypher Query:
        {vulnerability_cypher_context}

        Based on the provided context, perform your tasks.
        """
    ),
])
log_analysis_chain = log_analysis_prompt | llm.with_structured_output(LogAnalysisOutput)