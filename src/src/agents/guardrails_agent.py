# src/agents/guardrails_agent.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from src.config.settings import llm

class GuardrailsRouterOutput(BaseModel):
    """
    Combined output for guardrails checking and routing decisions
    """
    decision: Literal["relevant", "irrelevant"] = Field(
        description="Determine if the question falls within the scope of Vulnerability Assessment (Finding, Scoring, Prioritizing, Explaining)."
    )
    reason: str = Field(
        description="Brief explanation of why the question is relevant or irrelevant."
    )
    datasource: Literal["log_analysis", "cyber_knowledge"] = Field(
        description="Routes the question. 'log_analysis' for finding vulnerabilities in system logs/events. 'cyber_knowledge' for scoring, prioritizing, explaining CVEs/CWEs or general security concepts."
    )

guardrails_router_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        """
        You are the Main Guardrail Agent for a specialized **Vulnerability Assessment System**.
        Your job is to strictly filter user queries and route them correctly.

        **ALLOWED SCOPE (Vulnerability Assessment):**
        You should only allow questions related to:
        1. **Finding/Detection**: Identifying vulnerabilities, bugs, flaws, or suspicious patterns in software/logs (e.g., "Find SQL injection attempts in the logs", "What CVEs affect version X?").
        2. **Scoring**: Assessing severity, CVSS scores, or impact levels (e.g., "What is the CVSS score of CVE-2023-1234?", "Is this critical?").
        3. **Prioritizing**: Determining which vulnerabilities to fix first based on risk (e.g., "Which patch should I apply first?").
        4. **Explaining**: Understanding how a vulnerability works, technical details, and remediation/mitigation (e.g., "Explain how buffer overflow works", "How to fix Log4Shell").

        **FORBIDDEN TOPICS (Return 'irrelevant'):**
        - General chit-chat (e.g., "How are you?", "Who made you?").
        - Questions unrelated to cybersecurity (e.g., "What is the weather?", "Write a poem").
        - Requests to create malicious exploits for illegal attacks (Defensive analysis is OK, Offensive/Malicious creation is NOT).

        **ROUTING RULES (If relevant):**
        - **log_analysis**: Use this if the user wants to search for evidence of vulnerabilities or attacks inside **system logs**, specific events, IP addresses, or user activities.
        - **cyber_knowledge**: Use this for questions about **knowledge** concepts, specific CVE definitions, scoring, standard frameworks (MITRE, CAPEC), or best practices.

        Analyze the question carefully.
        """
    ),
    ("human", "Question: {question}"),
])

guardrails_router_chain = guardrails_router_prompt | llm.with_structured_output(GuardrailsRouterOutput)