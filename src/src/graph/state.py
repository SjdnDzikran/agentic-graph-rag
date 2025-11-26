from typing import List, TypedDict, Optional

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    """
    question: str
    generation: str
    documents: List[str]
    # --- Tambahkan field baru di bawah ini ---
    is_relevant: bool       # Apakah pertanyaan relevan dengan vuln assessment?
    guardrail_reason: str   # Alasan kenapa ditolak/diterima
    is_log_question: bool   # Apakah pertanyaan tentang log?
    log_vector_context: str
    log_cypher_context: str
    mcp_rdf_context: str
    generated_question_for_rdf: str