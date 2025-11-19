# src/chains/synthesizer.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from src.config.settings import llm

synthesis_prompt = ChatPromptTemplate.from_template("""You are an expert cybersecurity analyst creating a final report.
Your task is to synthesize information from a log analysis and a cybersecurity knowledge base to answer a user's question.

The final output MUST follow this exact structure. Do not add any text outside of this structure.
If a section is not applicable (e.g., no log data was queried), state "Not applicable for this query." in that section.

---
**1. Original Question:**
{original_question}

**2. Cypher Log Information Context:**
{log_cypher_context}

**3. Vector Log Information Context:**
{log_vector_context}

**4. Generated Question for Cybersecurity Knowledge Base:**
{generated_question_for_rdf}

**5. Cybersecurity Knowledge Base Context (from RDF Agent):**
{mcp_rdf_context}

**6. Critical Analysis:**
[Analyze how the information from all sources connects. Explain how the log events (if any) could be indicators of the cybersecurity concepts found. If only one source has data, analyze its sufficiency.]

**7. Contextual Linkage:**
[Explain the logical flow of the investigation. For example: "The initial query about user 'danette' led to the discovery of repeated authentication failures in the logs. This pattern prompted an inquiry into related attack techniques, which the knowledge base identified as a potential Brute Force attack (T1110)."]

**8. Final Answer:**
[Construct a final, well-structured, human-readable answer for the user. Synthesize all findings into a cohesive response.]
---
""")

synthesis_chain = synthesis_prompt | llm | StrOutputParser()
