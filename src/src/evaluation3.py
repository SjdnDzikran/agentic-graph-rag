# src/evaluation_week3.py
import asyncio
import time
import pandas as pd
import random
import logging

# Import your system components
from src.graph.workflow import app as agentic_app
from src.baselines.normal_rag import run_normal_rag
from src.baselines.cvss_lookup import CVSSBaseline
from src.utils.metrics import (
    extract_score, 
    get_severity_label, 
    calculate_spearman_rank_correlation, 
    calculate_classification_metrics
)

# Suppress verbose logs during eval
logging.getLogger("src.graph.workflow").setLevel(logging.ERROR)

async def get_agentic_response(question: str):
    """Helper to invoke the Agentic Graph RAG"""
    inputs = {"question": question, "original_question": question}
    config = {"recursion_limit": 50}
    
    try:
        # ainvoke is the async method for LangGraph applications
        result = await agentic_app.ainvoke(inputs, config=config)
        return result.get('answer', "No answer generated.")
    except Exception as e:
        return f"Error: {str(e)}"

async def run_experiments():
    # 1. Setup Data
    cvss_lookup = CVSSBaseline()
    # Get a random sample of CVEs (or specific ones for consistency)
    all_ids = cvss_lookup.df['id'].tolist()
    # Sampling 5 for a quick test, increase to 50-100 for final report
    test_cves = random.sample(all_ids, min(5, len(all_ids))) 
    
    results = []
    print(f"--- Starting Week 3 Evaluation on {len(test_cves)} CVEs ---")

    for cve_id in test_cves:
        print(f"\n[Eval] Processing {cve_id}...")
        
        # A. Ground Truth
        gt_data = cvss_lookup.get_vulnerability_details(cve_id)
        if not gt_data: continue
        gt_score = float(gt_data['cvss_score']) if gt_data['cvss_score'] else 0.0
        gt_severity = gt_data['severity'] if gt_data['severity'] else "UNKNOWN"

        query = f"What is the CVSS score and severity for {cve_id}?"

        # B. Normal RAG
        start_norm = time.time()
        norm_res = run_normal_rag(query)
        norm_time = time.time() - start_norm
        norm_text = norm_res['answer']
        
        # C. Agentic RAG
        start_agent = time.time()
        agent_text = await get_agentic_response(query)
        agent_time = time.time() - start_agent
        
        # D. Extraction
        norm_score_pred = extract_score(norm_text)
        agent_score_pred = extract_score(agent_text)
        
        norm_severity_pred = get_severity_label(norm_score_pred)
        # For agentic, we can try to extract severity text, or derive from score
        # Here we derive from score for consistency in comparison
        agent_severity_pred = get_severity_label(agent_score_pred) 

        results.append({
            "cve_id": cve_id,
            "gt_score": gt_score,
            "gt_severity": gt_severity,
            # Normal RAG
            "normal_score": norm_score_pred,
            "normal_severity": norm_severity_pred,
            "normal_time": norm_time,
            # Agentic RAG
            "agentic_score": agent_score_pred,
            "agentic_severity": agent_severity_pred,
            "agentic_time": agent_time
        })

    # 2. Calculate Aggregate Metrics
    df = pd.DataFrame(results)
    
    # Ranking Correlation (Spearman)
    # Compares how well the system ranks vulnerabilities (e.g. does it know Critical > Low)
    rho_normal = calculate_spearman_rank_correlation(df['gt_score'].tolist(), df['normal_score'].tolist())
    rho_agentic = calculate_spearman_rank_correlation(df['gt_score'].tolist(), df['agentic_score'].tolist())
    
    # Classification Metrics (Precision/Recall for Severity Labels)
    metrics_normal = calculate_classification_metrics(df['gt_severity'].tolist(), df['normal_severity'].tolist())
    metrics_agentic = calculate_classification_metrics(df['gt_severity'].tolist(), df['agentic_severity'].tolist())

    # 3. Display Final Report
    print("\n\n" + "="*40)
    print("       WEEK 3 EXPERIMENTAL RESULTS       ")
    print("="*40)
    
    print(f"\n1. Ranking Correlation (Spearman's Rho):")
    print(f"   - Normal RAG:  {rho_normal:.4f}")
    print(f"   - Agentic RAG: {rho_agentic:.4f} (Target: > Normal)")
    
    print(f"\n2. Accuracy Metrics (Severity Classification):")
    print(f"   - Normal RAG:  Acc={metrics_normal['accuracy']:.2f}, Prec={metrics_normal['macro_precision']:.2f}, Rec={metrics_normal['macro_recall']:.2f}")
    print(f"   - Agentic RAG: Acc={metrics_agentic['accuracy']:.2f}, Prec={metrics_agentic['macro_precision']:.2f}, Rec={metrics_agentic['macro_recall']:.2f}")
    
    print(f"\n3. Average Response Time (Latency):")
    print(f"   - Normal RAG:  {df['normal_time'].mean():.2f} seconds")
    print(f"   - Agentic RAG: {df['agentic_time'].mean():.2f} seconds")
    
    # Save detailed CSV for report
    df.to_csv("week3_results.csv", index=False)
    print(f"\nDetailed results saved to 'week3_results.csv'")

if __name__ == "__main__":
    asyncio.run(run_experiments())