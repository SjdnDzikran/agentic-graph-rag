# AgCyRAG: an Agentic Knowledge Graph based RAG Framework for Automated Security Analysis

## Authors
- **Kabul Kurniawan** (Department of Computer Science and Electronics, Universitas Gadjah Mada, Indonesia; Center for Cryptography and Cybersecurity Research, Universitas Gadjah Mada)
- **Rayhan Firdaus Ardian** (Department of Computer Science and Electronics, Universitas Gadjah Mada, Indonesia)
- **Elmar Kiesling** (WU Wien, Institute for Data, Process and Knowledge Management, Vienna, Austria)
- **Andreas Ekelhart** (SBA Research, Vienna, Austria; University of Vienna, Vienna, Austria)

**Contact**: kabul.kurniawan@ugm.ac.id

**Conference**: RAGE-KG 2025: The Second International Workshop on Retrieval-Augmented Generation Enabled by Knowledge Graphs, co-located with ISWC 2025, November 2–6, 2025, Nara, Japan

---

## Abstract

Cybersecurity analysis is a critical activity that aims to detect threats, respond to incidents, and ensure organizational resilience. It is a highly complex task where analysts typically navigate and interpret vast amounts of heterogeneous data across structured and unstructured sources, ranging from system logs and network activity logs to threat intelligence and policy documents. Large Language Models (LLMs) can provide simplified access to this data through a natural language interface and have the potential to unlock advanced analytic capabilities.

In this paper, we propose to combine a number of Retrieval-Augmented Generation (RAG) techniques to make this diverse and highly dynamic information accessible to LLMs and enable factual grounding of cybersecurity analyses. A key challenge in this context is that RAG approaches typically focus on unstructured text and often overlook symbolic representations and conceptual relations that are essential in cybersecurity – including network structures, IT assets hierarchies and attack patterns.

To address this gap, we propose **AgCyRAG**: a hybrid Agentic RAG framework that integrates Knowledge Graphs (KGs) and vector-based retrieval to enhance the factual accuracy and contextual relevance of security analyses. The framework orchestrates multiple agents that interpret user queries and adaptively select the optimal retrieval strategy according to the analytical context. The agentic workflows enable systems to combine structured semantic reasoning with vector-based retrieval, resulting in more comprehensive and interpretable security analyses.

We validate AgCyRAG by means of three real-world use-cases and demonstrate its ability to support advanced, context-aware security analyses.

**Keywords**: Agentic, RAG, LLM, Cybersecurity, Knowledge Graph

---

## 1. Introduction

Cybersecurity analysis is crucial for safeguarding digital infrastructures by enabling timely detection of threats, effective incident response, and sustained organizational resilience. However, as cyber threats become more sophisticated and widespread, interpreting vast volumes of heterogeneous data, such as system logs, network traffic, and threat intelligence reports, to detect and mitigate malicious activities, has become increasingly difficult. Moreover, this data spans both structured and unstructured formats and is often distributed across siloed systems, which makes timely and accurate analysis inherently challenging.

Recent advances in Large Language Models (LLMs) have created new opportunities to enhance cybersecurity operations by supporting defensive, offensive, vulnerability, and risk assessment activities. LLMs offer intuitive, natural language interfaces that can simplify the process of querying and synthesizing information from complex datasets. By understanding and generating human-like text, LLMs can assist analysts with tasks such as identifying suspicious behavior, correlating incidents, and reasoning about adversarial behavior. However, LLMs are prone to hallucinations and lack reliable mechanisms for grounding their outputs in verifiable evidence, which poses significant risks in high-stakes domains like cybersecurity.

To mitigate these limitations, Retrieval-Augmented Generation (RAG) has emerged as a promising technique to enrich the generative capabilities of LLMs by retrieving relevant external information from curated knowledge sources before generating a response. This improves factual grounding and reduces the likelihood of hallucinated or misleading outputs. Despite these advances, current RAG approaches primarily focus on unstructured data and typically process it as disconnected chunks of text. Security analytics, on the other hand, typically requires reasoning about complex cybersecurity knowledge in structured representations.

For instance, to understand whether a PowerShell command indicates an illegitimate login, it is necessary to contextualize it within a broader sequence of system events, user behavior, and known attack patterns. These forms of reasoning often involve multiple dispersed knowledge sources such as event sequences, network topologies, hierarchical asset models and attack patterns to be integrated for the purpose of, e.g., identifying the root cause of an attack and assessing the potential impact. Traditional RAG approaches are typically designed for document retrieval and do not account for neither symbolic and relational structures, nor temporal ones, hence, missing the deeper context behind relationships that are fundamental to cybersecurity.

### Key Contributions

To address this gap, we introduce **AgCyRAG**, a hybrid Agentic RAG framework specifically designed for cybersecurity analysis. AgCyRAG provides advanced retrieval paradigms that combine Knowledge Graph (KG)-based reasoning with vector based retrieval in an agentic framework to provide accurate, context-aware, and explainable analytical support.

Our contributions in this paper can be summarized as follows:

1. We propose an agentic framework for cybersecurity analysis
2. We integrate RAG techniques for log-structured data
3. We provide the LLMs performing the analyses with attack knowledge grounded in MITRE's ATT&CK framework
4. We assess the capabilities of LLM-based log analysis on synthetically generated data in common analytic scenarios (i.e., analyzing login data for suspicious behavior)
5. We demonstrate how the proposed framework can support human analysts and provide an effective and efficient natural language interface to initiate and perform agentic cybersecurity analyses

---

## 2. Related Work

The field of cybersecurity analysis has seen a shift towards leveraging knowledge-based systems and LLMs to handle the complexity and sheer volume of data. This section reviews key developments in two areas: (i) Cybersecurity Knowledge Graphs and Semantic Security Analysis, and (ii) LLMs in cybersecurity, RAG, and particularly the emerging field of agentic RAG for cybersecurity.

### Cybersecurity Knowledge Graphs and Semantic Analysis

The foundation for structured security analysis was laid by early research into cybersecurity ontologies and semantic approaches. These efforts aimed to create formal vocabularies and models to represent security knowledge in a machine-readable format. Foundational work proposed core ontologies to formalize security terminologies. Other research focused on more specific applications, such as:

- Modeling attacks for intrusion detection
- Annotating security resources
- Describing security incidents and requirements
- Semantic analysis of log data

Building on these early ontologies, the field shifted toward creating comprehensive cybersecurity knowledge graphs (CKGs) that could integrate and correlate diverse data sources. Notable developments include:

- **SEPSES Knowledge Graph**: Addresses the challenge of logs and threat intelligence integration
- **ICS-SEC KG**: Specialized for industrial control systems
- **ATT&CK-KG**: Links attacks to adversary tactics

Recent surveys have extensively reviewed the applications of CKGs, highlighting their potential for threat intelligence and automated reasoning by revealing connections that are otherwise difficult to detect.

### LLM, Retrieval-Augmented Generation and Agentic Frameworks

The advent of LLMs has introduced new possibilities for cybersecurity by enabling natural language interfaces and advanced reasoning capabilities. Broader surveys on LLMs discuss core concepts, architectures, and challenges like hallucination, which is a significant concern when using LLMs for fact-sensitive tasks like security analysis.

To overcome the limitations of relying solely on LLMs, RAG has emerged as a promising technique. Lewis et al. introduced the foundational concept of RAG, which combines a retriever (to find relevant information) with a generator (the LLMs) to produce more accurate, grounded responses. This approach has been adapted for cybersecurity:

- **CyKG-RAG**: Specifically leverages a knowledge graph for the retrieval step to provide LLMs with structured cybersecurity knowledge

More recently, the concept of **agentic RAG** has gained traction. This involves orchestrating multiple specialized agents to perform different tasks, such as querying databases, retrieving documents, and synthesizing information, in a dynamic workflow. Specific agentic frameworks for cybersecurity have been proposed:

- **ARCeR**: An agentic RAG for defining cyber ranges
- **CRAKEN**: An LLM agent with knowledge-based execution for cybersecurity

Our proposed AgCyRAG framework builds upon these ideas by creating a hybrid agentic system that intelligently combines structured knowledge graph reasoning (via Cypher and SPARQL agents) with vector-based retrieval to provide a more comprehensive and accurate approach to automated security analysis.

---

## 3. AgCy-RAG Framework

### 3.1. The Agentic KG-RAG Architecture

The AgCyRAG framework has a modular architecture that provides separate agents based on their functionality (task and role). The workflow orchestrates five specialized agents, each designed to handle specific aspects of the query pre-processing, query execution & retrieval, and response generation processes.

#### Workflow Overview

**Query pre-processing** is managed by a guardrail agent that filters irrelevant queries.

**Query execution** is handled by three specialized retrieval agents that coordinate retrieval from both local sources (such as event logs) and external cybersecurity knowledge graphs (KGs).

**Response generation** is performed by reflection and synthesize agents, which evaluate the generated response and integrate it into a coherent and relevant answer.

#### Agent Descriptions

**1. Guardrail Agent**

The workflow starts with a guardrail agent that filters incoming queries to ensure they address cybersecurity topics. Once the query passes the relevance check, the agent routes the query to the appropriate set of Retrieval Agents.

Internally, the Guardrail Agent also performs entity extraction through Named Entity Recognition (NER) to identify critical parameters such as:
- Usernames
- System names
- Dates
- IP addresses

These become search tokens for subsequent retrieval steps. Based on both the intent and the entities found, the Guardrail Agent determines the appropriate routing:
- Vector Agent for semantic similarity search
- Cypher Agent for structured log graph retrieval
- SPARQL Agent for CSKG related queries

This selective routing prevents unnecessary resource usage and ensures that only the relevant retrieval agents are triggered, maintaining efficiency and precision throughout the pipeline.

**2. Retrieval Agents**

The retrieval agents provide three types of retrieval services:

- **Vector Agent**: Specializes in performing semantic similarity retrieval over log graphs. This is achieved by mapping the processed query and extracted entities into a high-dimensional vector space (embeddings). The agent then searches an embedding index stored within a Labelled Property Graph (LPG) database to identify relevant log chunks. The Vector Agent contributes a crucial task when symbolic graph queries alone cannot capture nuanced or context-rich patterns that exist in unstructured raw log data.

- **Cypher Agent**: Operates on a LPG, which represents structured relationships extracted from raw log data, constructed from log data and events in local environments (e.g., System logs). Using the Cypher query language, this agent retrieves structured local insights about system events, network behaviors, and user activity.

- **SPARQL Agent**: Focuses on enriching the analysis with external cybersecurity intelligence. It connects to the CSKG, represented in Resource Description Framework (RDF) and accessed via a SPARQL endpoint. This KG integrates a variety of structured threat intelligence from standardized sources such as CVE, CWE, CAPEC and MITRE ATT&CK. The agent operates through Model Context Protocol (MCP), which allows the LLM to invoke predefined SPARQL query functions hosted on a MCP server.

**3. Reflection Agent**

Receives all retrieved evidence and conducts a reasoning pass to evaluate its coherence and relevance. This agent assesses the sufficiency of retrieved information, and decides whether additional refinement or retrieval rounds are necessary. It acts as a quality control loop.

For example, if log data shows suspicious activity but lacks contextual threat intelligence, it will trigger another retrieval from external log graphs such as CSKG. Once the Reflection Agent detects that the log and semantic search results point to suspicious activity but lack an explicit mapping to known attack techniques, it triggers the SPARQL Agent. Finally, when the contextual output is deemed satisfactory, it passes the output to the Synthesis Agent.

**4. Synthesis Agent**

Integrates and summarizes the findings into a coherent and human-readable answer. This synthesis process is grounded in RAG, using prompt templates and evidence injection strategies to generate structured, explainable responses. It merges structured log data, semantic search results, and threat intelligence into a single comprehensive answer.

### 3.2. Retrieval Mechanism

The retrieval mechanism is demonstrated through a security analysis use-case that aims to identify suspicious activity, map it to known attack patterns, and recommend potential mitigations.

#### Example Use Case: Detecting Suspicious Activity

**Query**: "Identify suspicious activity performed by user Daryl in the system, link the possible threat to attack patterns and the mitigation!"

**Step-by-Step Process**:

1. **Validation**: The Guardrail Agent validates the query's relevancy and performs entity extraction (User: Daryl, System)

2. **Vector Search**: Full-text search against the log graph stored in a LPG database (e.g., Neo4J). The Guardrail Agent routes to the Vector Agent for semantic similarity search.

3. **Reflection**: The Reflection Agent evaluates retrieved context from the Vector Agent. Logs reveal repeated authentication failures for user Daryl on February 29 at 15:38:42, indicating potential malicious activity.

4. **Cypher Query**: The Cypher agent generates a Cypher query to extract structured, security-relevant relationships from the log graph. Results show patterns of both authentication failures and successful logins for Daryl on the mail-0 system.

5. **Follow-up Question Generation**: The Reflection Agent determines whether further investigation with cybersecurity knowledge is required. It generates: "What attack patterns are associated with repeated authentication failures followed by a successful login, and what are the recommended mitigations for such scenarios?"

6. **SPARQL Query via MCP**: The SPARQL Agent leverages MCP to identify suitable tools for querying the CSKG. The tool `get_technique_by_keywords` is selected and executed, retrieving attack techniques like Credential Stuffing and Password Guessing. Then `get_mitigations_for_technique` retrieves mitigations such as Account Use Policies and Password Policies.

7. **Final Synthesis**: The Synthesis Agent merges information from all sources and produces a final interpretation with clear, human-readable security analysis.

---

## 4. Implementation and Use-Case Application

### 4.1. Implementation

**Prototype Availability**: https://github.com/sepses/multi-agents-cykg-rag

**Technical Stack**:
- **Orchestration**: LangGraph for multi-agent coordination
- **Backend Architecture**: Dual-graph approach
  - Labelled Property Graphs (LPG) for log graphs stored in Neo4j
  - RDF graphs for cybersecurity knowledge stored in Virtuoso triple store via SPARQL endpoint
- **Data Sources**:
  - Log data from AIT Log Dataset
  - SEPSES CSKG for cybersecurity knowledge (CVE, CWE, CPE, CVSS, CAPEC, ATT&CK)
- **Retrieval Mechanisms**:
  - Hybrid search combining Cypher graph query and semantic vector search
  - Hugging Face embeddings (all-MiniLM-L6-v2) for 384-dimensional vector space
- **Communication**: Model Context Protocol (MCP) for agent-CSKG interaction

**Example SPARQL Query** (MCP function `get_techniques_by_keyword`):

```sparql
PREFIX attack: <http://w3id.org/sepses/vocab/ref/attack#>
PREFIX dcterm: <http://purl.org/dc/terms/>

SELECT ?technique ?label WHERE {
  ?technique a attack:Technique .
  ?technique dcterm:title ?label .
  OPTIONAL { ?technique dcterm:description ?description }
  FILTER( CONTAINS(LCASE(?label), LCASE("{keyword}")) ||
          CONTAINS(LCASE(?description), LCASE("{keyword}")))
} ORDER BY ?label
LIMIT 50
```

### 4.2. Use Case Application

We evaluate our approach through three distinct use cases, each demonstrating different capabilities of the framework.

#### Use Case 1: General Cybersecurity Question

**Question**: "Which MITRE ATT&CK techniques are used by attackers to escalate their privileges within a network?"

**Agents Executed**:
- SPARQL Agent (MCP): `get_techniques_by_tactic('tactic_name': 'Privilege Escalation')`

**Agent Output**:
- technique: abuse-elevation-control-mechanism
- technique: access-token-manipulation
- technique: accessibility-features
- [Additional techniques...]

**Final Answer**: 
Attackers use a variety of techniques to escalate their privileges within a network, as outlined in the MITRE ATT&CK framework. These techniques include manipulating access tokens, exploiting accessibility features, modifying accounts, and bypassing user account controls, among others.

#### Use Case 2: Security Log Analysis without CSKG Context

**Question**: "Who is Daryl? What did he do on the system? What time he did it?"

**Agents Executed**:
- Vector Agent: Extracted Entities: ['Daryl', 'system']
- Cypher Agent: Query to retrieve user actions and timestamps

**Agent Outputs**:
- **Vector Output**: Raw log entries showing authentication events
- **Cypher Output**: Structured data showing AUTHENTICATION_FAILURE_ON and AUTHENTICATED_ON events for user 'daryl' on 'mail-0'

**Final Answer**: 
Daryl is a user who attempted to authenticate on the system 'mail-0'. According to the logs, Daryl experienced an authentication failure at 15:38:42 on February 29, as recorded in the documents. Subsequently, there was another authentication failure recorded at 15:39:01 on the same day. The logs do not provide a successful authentication timestamp for Daryl, indicating that his attempts to access the system may not have been successful.

#### Use Case 3: Security Log Analysis with CSKG Context

**Question**: "Identify suspicious activity performed by user Daryl in the system, link the possible threat to attack pattern and the mitigation!"

**Agents Executed**:
- Vector Agent: Extracted Entities: ['Daryl', 'system']
- Cypher Agent: Query for user activity patterns
- SPARQL Agent (MCP): 
  - `get_techniques_by_keyword('keyword': 'authentication failure')`
  - `get_mitigations_for_technique(technique_name': 'Credential Stuffing')`

**Agent Outputs**:
- **Vector Output**: Raw log entries with authentication failures
- **Cypher Output**: Structured activity showing AUTHENTICATION_FAILURE_ON, AUTHENTICATED_ON patterns
- **SPARQL Output**: 
  - Techniques: Credential Stuffing, Password Guessing
  - Mitigations: Account Use Policies, Multi-factor Authentication, Password Policies, Update Software

**Final Answer**: 
User Daryl's activity on the system 'mail-0' shows a pattern of repeated authentication failures followed by a successful login. This behavior is indicative of potential Credential Stuffing or Password Guessing attacks, where adversaries attempt to gain unauthorized access by trying multiple credentials. To mitigate such threats, it is recommended to implement account use policies that limit failed login attempts, enforce multi-factor authentication, establish strong password policies, regularly review user accounts, and keep software updated to protect against vulnerabilities. These measures can help prevent unauthorized access and enhance the security of user accounts.

---

## 5. Discussion

The three scenarios investigated demonstrate the ability and flexibility of the agentic framework to compose and orchestrate workflows for cybersecurity question answering and analysis.

### Key Findings

1. **Successful Integration**: The agentic workflows successfully retrieve and integrate information from:
   - Labeled property graphs (including vector embeddings)
   - Structured knowledge in triple stores
   - LLM-internal knowledge

2. **Improved Analysis Quality**: Comparing scenarios (ii) and (iii), granting the LLM access to structured knowledge about attack techniques and mitigations improves the answer from a plain description of suspicious behavior to explanations and actionable recommendations.

3. **Guided Workflows**: Structured knowledge on attack patterns provides a framework to guide more complex multi-step analytic workflows.

### Limitations

1. **Hallucination Risk**: Although the RAG-based approach and reflection agent successfully eliminated hallucinations in experiments, potential risks remain. Human analyst validation is still required.

2. **Predefined Query Constraints**: Analytic capabilities are constrained by reliance on predefined Cypher and SPARQL queries exposed via MCP, preventing LLM agents from executing arbitrary queries. While this improves answer quality, it limits free exploration of available knowledge.

3. **Task Complexity**: Current results focus on relatively straightforward tasks. More complex scenarios involving extended attack chains need further evaluation.

4. **Security Concerns**: Adversarial attacks on the agentic framework itself remain unexplored.

### Future Directions

- Expand to more complex scenarios beyond isolated analytic tasks
- Evaluate reasoning over extended attack chains
- Assess scalability of analyses
- Investigate agents with extended access for direct knowledge graph querying
- Explore adversarial attack resistance

---

## 6. Conclusions

In this paper, we presented **AgCyRAG**, a hybrid Agentic Retrieval-Augmented Generation framework that integrates vector-based retrieval with knowledge graph based querying mechanisms to enhance the accuracy, contextual relevance, and interpretability of security log analyses.

### Key Achievements

AgCyRAG successfully:
- Orchestrates multiple retrieval mechanisms in a dynamic, agent-driven workflow
- Bridges the gap between low-level security data and high-level cybersecurity knowledge
- Automatically refines queries based on intermediate findings
- Enables context-aware mapping of suspicious activities to attack patterns from the CSKG
- Produces evidence-grounded, human-readable analyses supporting operational decision-making

### Future Work

1. Comprehensive evaluations using various LLM models, datasets, and use cases
2. Testing in complex scenarios including multi-hop question answering
3. Expanding to other domains (vulnerability scanning, intrusion detection)
4. Assessing robustness, scalability, and adaptability under evolving threat landscapes

By combining symbolic and sub-symbolic retrieval within agentic orchestration, AgCyRAG takes an important step toward more reliable, interpretable, and operationally effective AI-assisted cybersecurity analysis.

---

## Acknowledgements

This work was supported by:
- Department of Computer Science and Electronics, Universitas Gadjah Mada (Publication Funding Year 2025)
- Austrian Research Promotion Agency (FFG) under "Digitale Technologien 2023" programme (FFG Project No. FO999915293 – LLM4CTI)
- SBA Research (SBA-K1 NGC) - COMET Center within the COMET Programme funded by BMIMI, BMWET, and the federal state of Vienna
- Austrian Science Fund (FWF) 10.55776/COE12

## Declaration on Generative AI

During the preparation of this work, the authors used ChatGPT for grammar and spelling checks. The authors reviewed and edited the content as needed and take full responsibility for the publication's content.

---

## References

[Complete reference list with 28 citations covering topics including:
- Cybersecurity ontologies and knowledge graphs
- Large Language Models and security applications
- Retrieval-Augmented Generation techniques
- Agentic frameworks for cybersecurity
- Related datasets and knowledge bases]