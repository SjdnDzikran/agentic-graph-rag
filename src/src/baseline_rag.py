from src.config.settings import vector_index, llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def run_baseline_rag(question: str):
    # 1. Retrieve (Vector Search Only)
    print(f"Searching for: {question}")
    docs = vector_index.similarity_search(question, k=3)
    context = "\n\n".join([d.page_content for d in docs])

    # 2. Generate
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"context": context, "question": question})

if __name__ == "__main__":
    print(run_baseline_rag("What is the CVE-2024-1234 vulnerability?"))