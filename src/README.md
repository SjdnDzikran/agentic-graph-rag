
# AgCyRAG: an Agentic Knowledge Graph based RAG Framework for Automated Security Analysis

AgCyRAG is a hybrid Agentic Retrieval-Augmented Generation (RAG) framework designed to improve cybersecurity analysis by integrating Knowledge Graph (KG) reasoning with vector-based retrieval.
It enables factual grounding of Large Language Model (LLM)-powered analyses while handling heterogeneous structured and unstructured data (e.g., security log sources).

## Architecture Overview

AgCyRAG uses a multi-agent architecture orchestrated by LangGraph, combining local and remote knowledge sources to provide comprehensive cybersecurity analysis.

### Agent Workflow

```
User Query
    ↓
[Guardrails & Router] ← Validates & routes questions
    ↓
    ├─→ [Vector Agent] ──────→ Neo4j (Semantic Search)
    ├─→ [Cypher Agent] ──────→ Neo4j (Graph Traversal)
    └─→ [MCP RDF Agent] ─────→ SEPSES SPARQL Endpoint
         ↓
    [Reflection Agent] ← Reviews if results are sufficient
         ↓
    [Synthesizer Agent] ← Combines all results into final answer
         ↓
    Final Answer
```

### Data Sources

The system queries **two independent knowledge graphs**:

#### 1. **Local Neo4j Database** (Your Machine)
- **Contains**: MITRE ATT&CK framework data, custom CVE datasets
- **Query Methods**: 
  - **Vector Search**: Semantic similarity using embeddings
  - **Cypher Queries**: Graph traversal for relationships
- **Connection**: Direct connection via Python `neo4j` driver
- **Data**: Loaded locally via `ingest_cve_dataset.py` script

#### 2. **Remote SEPSES SPARQL Endpoint** (TU Wien)
- **Endpoint**: `https://w3id.org/sepses/sparql`
- **Contains**: 
  - CVE (Common Vulnerabilities and Exposures)
  - CWE (Common Weakness Enumeration)
  - CAPEC (Common Attack Pattern Enumeration)
  - CPE (Common Platform Enumeration)
  - CVSS Scoring Metrics (v2 and v3)
- **Query Method**: SPARQL queries sent over HTTP
- **Connection**: Via MCP (Model Context Protocol) server
- **Data**: Live queries to remote RDF triplestore (no local download)
- **Maintained by**: SEPSES Project at Technical University of Vienna

### How It Works

1. **Question Processing**: The Guardrails agent validates the question and the Router determines which agents to invoke
2. **Parallel Querying**: Agents query their respective data sources simultaneously:
   - **Vector/Cypher Agents** → Query local Neo4j database
   - **MCP RDF Agent** → Sends SPARQL queries to remote SEPSES endpoint
3. **Reflection Loop**: If results are insufficient, agents iterate with refined queries
4. **Synthesis**: The Synthesizer combines all results into a coherent answer with source attribution

### Agent Communication

- **State Management**: All agents share a `GraphState` object that flows through the workflow
- **Orchestration**: LangGraph manages execution order using nodes, edges, and conditional routing
- **No Direct Agent-to-Agent Calls**: Communication happens through the shared state machine

## Core Components

- **Multi-Agent System (LangGraph)**: The primary application logic that orchestrates the entire workflow. It includes specialized agents for validating questions, querying databases, reflecting on results, and synthesizing final answers.
- **Neo4j Knowledge Graph**: A graph database storing structured cybersecurity data (e.g., from the MITRE ATT&CK framework), which is queried using the Cypher language.
- **MCP RDF Explorer**: Model Context Protocol (MCP) server that provides a conversational interface for RDF-based Knowledge Graph exploration using the SEPSES Cybersecurity Knowledge Graph via SPARQL endpoint. (Based on https://github.com/emekaokoye/mcp-rdf-explorer)

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.10+**: Required for running the application
2. **uv**: Fast Python package installer and resolver
   - Installation guide: https://docs.astral.sh/uv/getting-started/installation/
   - Quick install: `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS) or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows)
3. **Neo4j Database**: Either local instance or Neo4j Aura cloud
   - Local: Download from https://neo4j.com/download/
   - Cloud: Sign up at https://neo4j.com/cloud/aura/ (free tier available)
4. **API Keys**:
   - **Google Gemini API**: For LLM capabilities (https://makersuite.google.com/app/apikey)
   - **LangChain API** (optional): For tracing and monitoring (https://smith.langchain.com/)

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <this-repository-url>
cd agentic-graph-rag
```

### 2. Install Dependencies

```bash
uv sync
```

This will create a virtual environment and install all required dependencies.

### 3. Configure Neo4j

**Option A: Local Neo4j**
1. Install and start Neo4j Desktop or Community Edition
2. Create a new database
3. Note your connection details (default: `bolt://localhost:7687`, username: `neo4j`)

**Option B: Neo4j Aura (Cloud)**
1. Create a free account at https://neo4j.com/cloud/aura/
2. Create a new instance
3. Save your connection URI, username, and password

### 4. Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_google_api_key_here

# Optional: LangChain Tracing (for debugging)
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=agentic-graph-rag

# Neo4j Local Database (if using local Neo4j)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD_ICS=your_neo4j_password_here
NEO4J_DATABASE=neo4j

# Neo4j Aura Cloud (if using Neo4j Aura instead)
NEO4J_AURA=neo4j+s://your-instance-id.databases.neo4j.io
NEO4J_AURA_USERNAME=neo4j
NEO4J_AURA_PASSWORD=your_aura_password_here
NEO4J_AURA_DATABASE=neo4j
```

**Important Notes:**
- At minimum, you need `GOOGLE_API_KEY` and either the local Neo4j or Aura credentials
- LangChain API is optional and only needed for tracing/debugging
- The system will use local Neo4j by default; Aura credentials are used as fallback

### 5. Configure SEPSES MCP Server

The SEPSES Cybersecurity Knowledge Graph MCP server is bundled in this repository (`src/mcp-cskg-rdf`).

Create a `browser_mcp.json` file in the project root:

```json
{
  "mcpServers": {
    "sepses_kg": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "scripts.run_sepses_mcp",
        "--sparql-endpoint",
        "https://w3id.org/sepses/sparql"
      ]
    }
  }
}
```

This configuration uses the public SEPSES SPARQL endpoint, which provides access to cybersecurity data including CVE, CWE, CAPEC, and CPE information.

**Offline Mode (Optional):**
If you prefer to work offline or want faster queries:
1. Download an RDF dump from https://w3id.org/sepses/dumps/
2. Update the `browser_mcp.json` to use the local file:
   ```json
   {
     "mcpServers": {
       "sepses_kg": {
         "command": "uv",
         "args": [
           "run",
           "python",
           "-m",
           "scripts.run_sepses_mcp",
           "--rdf-file",
           "path/to/your/sepses-dump.ttl"
         ]
       }
     }
   }
   ```

### 6. Populate Neo4j with Sample Data

Load the CVE dataset into Neo4j (this creates vector, keyword, and entity indexes automatically):

```bash
cd src
uv run python -m scripts.ingest_cve_dataset --csv ../data/cve_dataset.csv
```

This step imports sample cybersecurity data that the system will query alongside the SEPSES knowledge graph.

## Running the Application

### Basic Usage

From the `src` directory:

```bash
uv run -m src.run "Your cybersecurity question here"
```

### Example Queries

Try these example queries to test the system:

**CVE Queries:**
```bash
# Find vulnerabilities in specific products
uv run -m src.run "Show me CVEs affecting Apache products"
uv run -m src.run "Find vulnerabilities in Windows products"

# Search by severity
uv run -m src.run "Show me high severity vulnerabilities with CVSS score above 7.0"
uv run -m src.run "List recent CVEs with their descriptions"

# Search by keyword
uv run -m src.run "Find all CVEs mentioning OpenSSL"
uv run -m src.run "What are the highest-rated CVEs related to buffer overflow?"
```

**MITRE ATT&CK Queries (from Neo4j):**
```bash
uv run -m src.run "What are the most common attack techniques?"
uv run -m src.run "Show me attack patterns related to privilege escalation"
```

**Note:** The MCP server must be running for CVE/CWE/CAPEC queries. It starts automatically when you run a query.

## Troubleshooting

### Common Issues

**1. "No module named 'xyz'" error**
```bash
# Reinstall dependencies
uv sync --reinstall
```

**2. Neo4j connection errors**
- Verify Neo4j is running: Check Neo4j Desktop or Aura console
- Check credentials in `.env` file
- For local Neo4j, ensure it's listening on `bolt://localhost:7687`
- For Aura, use the full connection string starting with `neo4j+s://`

**3. "GOOGLE_API_KEY not found" error**
- Ensure your `.env` file is in the correct location (project root)
- Get an API key from https://makersuite.google.com/app/apikey
- Add it to `.env` as: `GOOGLE_API_KEY=your_key_here`

**4. MCP server not starting**
- The server starts automatically with the first query
- Check `browser_mcp.json` is in the project root
- Verify the SPARQL endpoint is accessible: https://w3id.org/sepses/sparql

**5. Empty results for CVE queries**
- The SEPSES endpoint may not have data matching very specific criteria
- Try broader queries like "Show me high severity CVEs" instead of "Critical OpenSSL CVEs from last 5 years"
- Check the CVSS threshold (9.0 is very high; try 7.0 for more results)

### Getting Help

- Check the logs in `src/log/` for detailed error messages
- Review the [query examples](../query-examples.md) for working SPARQL patterns
- Ensure all prerequisites are properly installed and configured

## Understanding SPARQL Namespaces and Schema Discovery

### How We Determined the Correct Namespaces

When working with external SPARQL endpoints like SEPSES, discovering the correct namespaces and properties requires systematic exploration:

#### 1. **Official Documentation**
The SEPSES project provides documentation about their ontology:
- Research Paper: *"SEPSES: A Framework for Semantic Preserving Data Enrichment"* (See `docs/978-3-030-30796-7_13.md`)
- Project Website: https://w3id.org/sepses/
- Vocabulary Documentation: https://w3id.org/sepses/vocab/

#### 2. **SPARQL Endpoint Introspection**
You can query the endpoint to discover its schema:

```sparql
# Discover all classes (entity types)
SELECT DISTINCT ?class (COUNT(?instance) AS ?count)
WHERE {
  ?instance a ?class .
}
GROUP BY ?class
ORDER BY DESC(?count)
```

```sparql
# Explore properties of a specific class (e.g., CVE)
PREFIX cve: <http://w3id.org/sepses/vocab/ref/cve#>
SELECT DISTINCT ?property (COUNT(?value) AS ?count)
WHERE {
  ?cve a cve:CVE .
  ?cve ?property ?value .
}
GROUP BY ?property
ORDER BY DESC(?count)
```

```sparql
# Find all namespaces used in the dataset
SELECT DISTINCT ?namespace
WHERE {
  ?s ?p ?o .
  BIND(REPLACE(STR(?s), "(.*[/#])[^/#]*$", "$1") AS ?namespace)
}
LIMIT 100
```

#### 3. **Standard Ontology Patterns**
Semantic Web follows conventions:
- **Dublin Core Terms** (`dcterms:`): Standard metadata (description, issued, modified, identifier)
- **FOAF** (`foaf:`): People and organizations
- **SKOS** (`skos:`): Taxonomies and controlled vocabularies
- **RDF/RDFS** (`rdf:`, `rdfs:`): Core RDF concepts (type, label, comment)

#### 4. **Trial and Error with Validation**
Test queries with educated guesses based on domain knowledge:
```sparql
# Wrong property name
?cve cve:cveId ?id .           # ❌ Returns no results

# Correct property name  
?cve cve:id ?id .              # ✅ Returns results
```

#### 5. **Working Examples as Schema Reference**
The [query-examples.md](../query-examples.md) file contains verified queries that serve as a "schema by example". These were validated against the live endpoint and document the correct property mappings.

### Key SEPSES Namespace Patterns

All SEPSES vocabularies include `/ref/` in their URI path:
```
✅ Correct: http://w3id.org/sepses/vocab/ref/cve#
❌ Wrong:   http://w3id.org/sepses/vocab/cve#
```

**Critical Property Mappings:**
- CVE ID: `cve:id` (not `cve:cveId`)
- Description: `dcterms:description` (not `cve:description`)
- Published Date: `dcterms:issued` (not `dcterms:created`)
- CVSS Score: `cvss:baseScore` (accessed via `cve:hasCVSS3BaseMetric`)

### Why This Matters

Understanding namespace discovery is crucial because:
1. **No Universal Standard**: Different RDF datasets use different vocabularies
2. **Documentation Gaps**: Not all endpoints have complete documentation
3. **Query Accuracy**: Wrong namespaces = empty results or errors
4. **Debugging**: Knowing how to explore helps troubleshoot issues

For this project, we documented all working namespaces in the MCP server (`src/mcp-cskg-rdf/src/mcp-cskg-rdf/server.py`) as a resource that the AI agent can reference when generating queries.


## Features

- **Multi-agent workflow**: Uses LangGraph to manage the workflow between agents (guardrails, vector search, cypher search, MCP RDF, reflection, and synthesizer).

- **Guardrails**: Ensures the questions asked are relevant to the cybersecurity domain.

- **Vector & Cypher Search**: Searches for answers from a vector and graph database (Neo4j) with automatic iteration and reflection if results are insufficient.

- **MCP RDF Agent**: Integrates RDF-based search to enrich the context of answers.

- **Synthesizer**: Combines results from multiple sources into a comprehensive final answer.

- **Logging & Configuration**: Supports structured logging and configuration via .env files.


## Project Structure

```bash

no-log-multi-agents-cykg-rag/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── mcp_rdf_agent.py
│   │   ├── cypher_agent.py
│   │   ├── reflection_agents.py
│   │   └── vector_agent.py
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── guardrails.py
│   │   ├── review.py
│   │   └── synthesizer.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py
│   │   └── workflow.py
│   ├── log/
│   │   └── (a log file will be created here)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging_config.py
│   └── run.py
└── .env


```