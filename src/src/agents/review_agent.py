# src/chains/review.py 
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class ReviewOutput(BaseModel):
    """Decision model for reviewing the sufficiency of vulnerability assessment data."""
    decision: Literal["sufficient", "insufficient"] = Field(
        description="Is the provided vulnerability context sufficient to answer the user's question about CVE, CWE, CAPEC, or security risks?"
    )
    reasoning: str = Field(
        description="A brief explanation for the decision, referencing specific vulnerability data points if present."
    )

review_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in evaluating vulnerability assessment information. Your task is to determine if the provided 'Context' contains concrete, factual vulnerability data that helps to answer the 'Original Question'. The context is 'sufficient' if it provides at least one factual data point relevant to the question (e.g., CVE ID, CVSS score, CWE weakness, CAPEC attack pattern, mitigation strategy, or affected product), even if it's not a complete answer. It is 'insufficient' only if it's completely empty or contains no relevant vulnerability information."),
    ("human", "Original Question: {question}\\n\\nContext:\\n{context}\\n\\nBased on this definition, is the context sufficient for vulnerability assessment?"),
])
review_chain = review_prompt | llm.with_structured_output(ReviewOutput)