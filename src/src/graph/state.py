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