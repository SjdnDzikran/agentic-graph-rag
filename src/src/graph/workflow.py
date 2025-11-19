# ... import yang sudah ada ...
from src.agents.guardrails_agent import guardrails_node  # <--- Import baru

# ... kode inisialisasi workflow ...
workflow = StateGraph(GraphState)

# 1. Tambahkan Node
workflow.add_node("guardrails", guardrails_node)
workflow.add_node("vector_search", vector_agent_node) 
# ... node lainnya ...

# 2. Tentukan Entry Point (Mulai dari Guardrails dulu)
workflow.set_entry_point("guardrails")

# 3. Buat Fungsi Logika Percabangan
def check_guardrails(state: GraphState):
    if state["is_relevant"]:
        return "proceed" # Lanjut ke pencarian
    else:
        return "stop"    # Berhenti karena OOT

# 4. Pasang Conditional Edge
workflow.add_conditional_edges(
    "guardrails",
    check_guardrails,
    {
        "proceed": "vector_search",  # Jika relevan, lanjut cari data
        "stop": END                  # Jika tidak, langsung selesai
    }
)

# ... sisa sambungan edge lainnya (vector -> synthesizer dll) ...