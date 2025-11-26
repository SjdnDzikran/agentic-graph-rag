# src/agents/mcp_rdf_agent.py
import os
import logging
from pathlib import Path
from mcp_use import MCPAgent, MCPClient
from src.config.settings import llm

logger = logging.getLogger(__name__)

# --- Konfigurasi dan Inisialisasi Agen MCP ---

_mcp_client = None

def get_mcp_client():
    """Inisialisasi dan mengembalikan MCPClient (hanya sekali)."""
    global _mcp_client
    if _mcp_client is None:
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "browser_mcp.json"
        if not config_path.exists():
            raise FileNotFoundError(f"MCP config file not found at {config_path}")
        os.environ["MCP_USE_ANONYMIZED_TELEMETRY"] = "false"
        _mcp_client = MCPClient.from_config_file(str(config_path))
    return _mcp_client

strict_system_prompt = """
You are a specialized cybersecurity assistant. You MUST answer questions ONLY by using the provided tools. Your only source of information is the knowledge graph accessed via tools.

Your thought process MUST be:
    1.  **Analyze the user's question** to understand the core intent.
    2.  **Select the best tool.**.
    3.  **Execute the tool.**  If that fails or the question is complex, use `text_to_sparql` to convert the question into a precise SPARQL query.
    4.  **Analyze the result.**
        - If the result is a **validation error** (like a Pydantic error), it means you provided the wrong arguments to the tool. Read the error message carefully. DO NOT use the same tool with the exact same arguments again. Correct the arguments and retry. For tools requiring `ctx`, DO NOT provide a value for it; the system handles it.
        - If the result is **empty or "not found"**, the information may not exist, or your query was too narrow. Try rephrasing your input for the tool, perhaps using a broader term.
        - If you are stuck in a loop of failures, only then you must state that you could not find the information.
    5.  **NEVER provide an answer from memory.** All answers must be based on tool results.
"""

async def run_mcp_agent(question: str) -> str:
    """
    Runs the MCPAgent with the given question and returns the result.
    """
    try:
        client = get_mcp_client()
        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=30,
            verbose=True,
            system_prompt=strict_system_prompt
        )
        result = await agent.run(question)
        return result
    except Exception as e:
        logger.error(f"An error occurred while running the MCP Agent: {e}")
        return f"Error during MCP agent execution: {e}"