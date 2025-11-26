from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class RouteQuery(BaseModel):
    """ 
    Routes the user's question to the appropriate tool
    """
    datasource: Literal["vulnerability_analysis", "weakness_knowledge"] = Field(
        description="Given the user question, route it to the 'vulnerability_analysis' tool if it is about specific CVE vulnerabilities, CVSS scoring, exploitability analysis, or affected products, or to 'weakness_knowledge' if it is about CWE weaknesses, CAPEC attack patterns, or mitigation strategies."
    )
    
router_prompt = ChatPromptTemplate.from_messages([
    (
        
        "system",
        """You are an expert at routing a user's question to the appropriate vulnerability assessment tool.

        Follow these rules:
        1.  **Prioritize Vulnerability Analysis**: If the question is related to specific CVE vulnerabilities, CVSS scores, exploitability metrics, vulnerability ranking, or affected products/vendors, ALWAYS route it to 'vulnerability_analysis'.
        2.  **Use Weakness Knowledge for General Queries**: If the question is about CWE weakness types, CAPEC attack patterns, mitigation strategies, or general security knowledge, route it to 'weakness_knowledge'.
        
        """
    ),
    (
        "human", 
        "Question: {question}"
    ),
])
router_chain = router_prompt | llm.with_structured_output(RouteQuery)