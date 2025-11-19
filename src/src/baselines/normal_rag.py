# src/baselines/normal_rag.py
import time
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config.settings import vector_index, llm

def run_normal_rag(question: str, k: int = 4):
    """
    Performs a standard RAG retrieval and generation.
    1. Retrieve top-k similar documents from Neo4j Vector Index.
    2. Generate answer using LLM.
    """
    start_time = time.time()
    
    # 1. Retrieval (Vector Only)
    print(f"[Normal RAG] Searching for: {question}")
    docs = vector_index.similarity_search(question, k=k)
    
    if not docs:
        return {
            "answer": "No relevant documents found.",
            "context": [],
            "latency": time.time() - start_time
        }

    # Concatenate context
    context_text = "\n\n".join([f"[Source: {d.metadata.get('id', 'Unknown')}] {d.page_content}" for d in docs])

    # 2. Generation
    template = """You are a cybersecurity analyst. Answer the question based ONLY on the following context. 
    If the answer is not in the context, state that you do not know.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"context": context_text, "question": question})
    
    return {
        "answer": response,
        "context": [d.page_content for d in docs],
        "latency": time.time() - start_time
    }

if __name__ == "__main__":
    # Test run
    result = run_normal_rag("What is the severity of the POODLE vulnerability?")
    print(f"\nAnswer: {result['answer']}")
    print(f"Latency: {result['latency']:.2f}s")