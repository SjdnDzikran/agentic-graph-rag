from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from src.graph.state import GraphState

# 1. Definisikan Struktur Output agar jawabannya pasti (True/False)
class GuardrailsOutput(BaseModel):
    is_relevant: bool = Field(
        description="True if the query is related to vulnerability assessment, cybersecurity, CVEs, or software security. False otherwise."
    )
    reason: str = Field(
        description="Brief explanation why the query is relevant or not."
    )

def guardrails_node(state: GraphState):
    """
    Agent untuk memvalidasi apakah pertanyaan user relevan dengan Vulnerability Assessment.
    """
    print("---GUARDRAILS CHECK---")
    question = state["question"]

    # 2. Setup LLM (Gunakan model yang cepat & murah)
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
    
    # 3. Prompt Khusus Vulnerability Assessment
    system_prompt = """You are a strict Guardrails Agent for a Vulnerability Assessment System.
    Your job is to filter user queries.
    
    ALLOWED TOPICS (Return is_relevant=True):
    - Finding/Detecting software vulnerabilities (CVEs, bugs, flaws).
    - Scoring vulnerabilities (CVSS scores, severity levels).
    - Prioritizing vulnerabilities (risk assessment, what to fix first).
    - Explaining vulnerabilities (how an exploit works, remediation, patches).
    - General cybersecurity concepts related to defense and analysis.
    - Asset Inventory (servers, laptops, devices).
    - Software Versions and Installed Applications.
    
    FORBIDDEN TOPICS (Return is_relevant=False):
    - General conversational chit-chat (e.g., "How are you?", "Weather").
    - Creating malicious code or exploit scripts for illegal purposes (Finding/Explaining is OK, Creating attacks is NOT).
    - Non-technical topics (Cooking, Sports, Politics).
    
    Analyze the user question and determine if it fits the ALLOWED TOPICS.
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])

    # 4. Chain dengan Structured Output
    structured_llm = llm.with_structured_output(GuardrailsOutput)
    chain = prompt | structured_llm

    result = chain.invoke({"question": question})

    # 5. Simpan keputusan ke State
    print(f"---GUARDRAILS DECISION: {result.is_relevant} ({result.reason})---")
    
    return {
        "is_relevant": result.is_relevant,
        "guardrail_reason": result.reason,
        # Jika tidak relevan, kita bisa langsung isi 'generation' dengan pesan penolakan
        "generation": result.reason if not result.is_relevant else state.get("generation")
    }