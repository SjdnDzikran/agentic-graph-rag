# src/chains/synthesizer.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from src.config.settings import llm

synthesis_prompt = ChatPromptTemplate.from_template("""You are an expert vulnerability assessment analyst creating a final report.
Your task is to synthesize information from vulnerability analysis and weakness knowledge base to answer a user's question.

The final output MUST follow this exact structure. Do not add any text outside of this structure.
If a section is not applicable (e.g., no vulnerability data was queried), state "Not applicable for this query." in that section.

---
**1. Original Question:**
{original_question}

**2. Cypher Vulnerability Information Context:**
{vulnerability_cypher_context}

**3. Vector Vulnerability Information Context:**
{vulnerability_vector_context}

**4. Generated Question for Weakness Knowledge Base:**
{generated_question_for_weakness_kb}

**5. Weakness Knowledge Base Context (CWE/CAPEC with Mitigation Strategies):**
{weakness_kb_context}

**6. Risk Assessment:**
[Analyze the severity and exploitability of identified vulnerabilities. Evaluate CVSS scores, exploit availability, and potential business impact. Explain how the vulnerability data connects with identified weaknesses (CWE) and attack patterns (CAPEC). If only one source has data, analyze its sufficiency for risk evaluation.]

**7. Attack Path Analysis:**
[Explain the logical attack chain from vulnerability to exploitation. For example: "CVE-2024-1234 with CVSS score 9.8 is linked to CWE-79 (Cross-Site Scripting). This weakness enables CAPEC-18 (XSS via HTML Injection), which could allow attackers to steal user credentials or session tokens."]

**8. Mitigation Recommendations:**
[Provide specific, actionable mitigation strategies based on CWE/CAPEC guidance. Prioritize recommendations by risk level. Include both immediate patches and long-term preventive measures.]

**9. Final Answer:**
[Construct a final, well-structured, human-readable answer for the user. Synthesize all findings into a cohesive vulnerability assessment report with clear risk prioritization.]
---
""")

synthesis_chain = synthesis_prompt | llm | StrOutputParser()
