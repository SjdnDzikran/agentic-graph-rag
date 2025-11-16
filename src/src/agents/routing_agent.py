from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class RouteQuery(BaseModel):
    """ 
    Routes the user's question to the appropriate tool
    """
    datasource: Literal["log_analysis", "cyber_knowledge"] = Field(
        description="Given the user question, route it to the 'log_analysis' tool if it is about log analysis and specific question related to log in the system or to 'cyber_knowledge' if it is a general cybersecurity question."
    )
    
router_prompt = ChatPromptTemplate.from_messages([
    (
        
        "system",
        """You are an expert at routing a user's question to tool.

        Follow these rules:
        1.  **Prioritize Log Analysis**: If the question related to log analysis and anything about events in log, ALWAYS route it to 'log_analysis'.
        2.  **Use Cyber Knowledge for General Queries**: If the question is about a general cybersecurity information and threat intelligence,  route it to 'cyber_knowledge'.
        
        """
    ),
    (
        "human", 
        "Question: {question}"
    ),
])

router_chain = router_prompt | llm.with_structured_output(RouteQuery)