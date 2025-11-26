import logging
from langgraph.graph import StateGraph, END
from src.graph.state import GraphState
from src.agents.guardrails_agent import guardrails_node
from src.agents.routing_agent import router_chain
from src.agents.vector_agent import query_vector_search
from src.agents.cypher_agent import query_cypher
from src.agents.mcp_rdf_agent import run_mcp_agent
from src.agents.synthesizer_agent import synthesis_chain

# Configure logging
logger = logging.getLogger(__name__)

# --- Node Wrappers ---

def router_node(state: GraphState):
    """
    Node to route the query based on the router agent's decision.
    """
    logger.info("--- Executing Node: [[Router]] ---")
    question = state["question"]
    result = router_chain.invoke({"question": question})
    
    is_log = result.datasource == "log_analysis"
    logger.info(f"[[Router]]: Routing decision: {result.datasource} -> is_log_question: {is_log}")
    
    return {"is_log_question": is_log}

def vector_agent_node(state: GraphState):
    """
    Node to perform vector search on logs.
    """
    logger.info("--- Executing Node: [[Vector Agent]] ---")
    question = state["question"]
    result = query_vector_search(question)
    return {"log_vector_context": result}

def cypher_agent_node(state: GraphState):
    """
    Node to perform Cypher query on Neo4j.
    """
    logger.info("--- Executing Node: [[Cypher Agent]] ---")
    question = state["question"]
    try:
        result = query_cypher(question)
        return {"log_cypher_context": result["context"]}
    except Exception as e:
        logger.error(f"Error in Cypher Agent: {e}")
        return {"log_cypher_context": f"Error: {e}"}

async def mcp_rdf_agent_node(state: GraphState):
    """
    Node to query the MCP RDF Agent.
    """
    logger.info("--- Executing Node: [[mcp_rdf_agent]] ---")
    question = state["question"]
    
    # Use generated question if available, else original
    question_to_ask = state.get("generated_question_for_rdf") or question
    logger.info(f"[[MCP RDF Agent]]: Answering question: '{question_to_ask}'")
    
    result = await run_mcp_agent(question_to_ask)
    logger.info(f"[[MCP RDF Agent]]: Search completed. Context found:\n{result}")
    return {"mcp_rdf_context": result}

def synthesizer_node(state: GraphState):
    """
    Node to synthesize the final answer.
    """
    logger.info("--- Executing Node: [[Synthesizer]] ---")
    inputs = {
        "original_question": state["question"],
        "log_cypher_context": state.get("log_cypher_context", "Not applicable"),
        "log_vector_context": state.get("log_vector_context", "Not applicable"),
        "generated_question_for_rdf": state.get("generated_question_for_rdf", "Not applicable"),
        "mcp_rdf_context": state.get("mcp_rdf_context", "Not applicable")
    }
    result = synthesis_chain.invoke(inputs)
    return {"generation": result}

# --- Conditional Logic ---

def decide_relevance(state: GraphState):
    """
    Determines the next node based on guardrails and router.
    """
    if not state.get("is_relevant", False):
        logger.info("[Decision] Question is irrelevant, ending execution.")
        return END
    
    if state.get("is_log_question", False):
        logger.info("[Decision] Question is about logs, proceeding to vector search.")
        return "vector_agent"
    else:
        logger.info("[Decision] Question is about cyber knowledge, proceeding to MCP RDF agent.")
        return "mcp_rdf_agent"

# --- Graph Construction ---

workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("guardrails", guardrails_node)
workflow.add_node("router", router_node)
workflow.add_node("vector_agent", vector_agent_node)
workflow.add_node("cypher_agent", cypher_agent_node)
workflow.add_node("mcp_rdf_agent", mcp_rdf_agent_node)
workflow.add_node("synthesizer", synthesizer_node)

# Set Entry Point
workflow.set_entry_point("guardrails")

# Add Edges
workflow.add_edge("guardrails", "router")

# Router -> Decision -> Next Node
workflow.add_conditional_edges(
    "router",
    decide_relevance,
    {
        "vector_agent": "vector_agent",
        "mcp_rdf_agent": "mcp_rdf_agent",
        END: END
    }
)

# For Log Analysis: Vector -> Cypher -> Synthesizer
# This ensures both agents run for log questions.
workflow.add_edge("vector_agent", "cypher_agent")
workflow.add_edge("cypher_agent", "synthesizer")

# For Cyber Knowledge: MCP -> Synthesizer
workflow.add_edge("mcp_rdf_agent", "synthesizer")

# Synthesizer -> End
workflow.add_edge("synthesizer", END)

# Compile
app = workflow.compile()