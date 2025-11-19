# src/chains/review.py 
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class ReviewOutput(BaseModel):
    """Decision model for reviewing the sufficiency of an answer."""
    decision: Literal["sufficient", "insufficient"] = Field(description="Is the provided context sufficient to answer the user's question?")
    reasoning: str = Field(description="A brief explanation for the decision.")

review_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in evaluating retrieved information. Your task is to determine if the provided 'Context' contains concrete, factual information that helps to answer the 'Original Question'. The context is 'sufficient' if it provides at least one factual data point relevant to the question, even if it's not a complete answer. It is 'insufficient' only if it's completely empty or irrelevant."),
    ("human", "Original Question: {question}\\n\\nContext:\\n{context}\\n\\nBased on this definition, is the context sufficient?"),
])
review_chain = review_prompt | llm.with_structured_output(ReviewOutput)