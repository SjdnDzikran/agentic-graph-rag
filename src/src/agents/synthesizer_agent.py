# src/chains/synthesizer.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from src.config.settings import llm

synthesis_prompt = ChatPromptTemplate.from_template("""
You receive:
- security findings from logs,
- mapped MITRE ATT&CK techniques,
- CVE entries with CVSS scores from the CSKG tool.

Task:
1. Explain what happened in the attack in clear steps.
2. For each vulnerability (CVE), show a row:
   - CVE ID
   - CVSS base score
   - severity
   - short description
3. Sort the table by CVSS base score descending.
4. Highlight the top 3 highest-risk findings and recommend mitigations.
""")

synthesis_chain = synthesis_prompt | llm | StrOutputParser()
