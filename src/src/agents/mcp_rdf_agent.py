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
        config_path = None
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "browser_mcp.json"
            if candidate.exists():
                config_path = candidate
                break
        if config_path is None:
            raise FileNotFoundError("MCP config file not found in current or parent directories.")
        os.environ["MCP_USE_ANONYMIZED_TELEMETRY"] = "false"
        _mcp_client = MCPClient.from_config_file(str(config_path))
    return _mcp_client

strict_system_prompt = """
You are a specialized vulnerability assessment assistant grounded in the Vulnerability Assessment Knowledge Graph.
Answer questions ONLY via the available tools, which surface data from the Neo4j graph database 
(CVE, CVSS scores, CWE, CAPEC, exploitability metrics, affected products, mitigation strategies, etc.).

Workflow:
1. Analyze the user's intent regarding vulnerability assessment, risk scoring, or mitigation strategies.
2. Select the most appropriate tool. Prefer the focused helper tools when possible.
3. Execute the tool. When you must run an ad-hoc Cypher query, call `text_to_cypher`
   and pass the natural language question to generate the appropriate Cypher statement.
4. Inspect the results:
   - Validation errors mean you supplied invalid arguments—adjust and retry.
   - Empty results mean the vulnerability data may not exist or the query is too specific—broaden or try another tool.
5. Never answer from memory; every statement must trace back to tool output from the knowledge graph.
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
