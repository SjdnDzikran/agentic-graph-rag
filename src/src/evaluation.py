# src/evaluation.py
import pandas as pd
import json
from src.baselines.normal_rag import run_normal_rag
from src.baselines.cvss_lookup import CVSSBaseline

def run_comparison():
    # 1. Define Test Cases (CVE IDs to query)
    # Ideally, select these randomly from your dataset
    test_cves = ["CVE-2014-3566", "CVE-2015-7548", "CVE-2002-0059"] 
    
    cvss_lookup = CVSSBaseline()
    results = []

    print("--- Starting Comparison Framework ---")

    for cve_id in test_cves:
        print(f"\nProcessing {cve_id}...")
        
        # A. Ground Truth (Traditional CVSS)
        ground_truth = cvss_lookup.get_vulnerability_details(cve_id)
        
        # B. Normal RAG Prediction
        # We ask a question similar to what a user would ask
        question = f"What is the severity and risk score of {cve_id}?"
        rag_result = run_normal_rag(question)
        
        # C. Record Result
        results.append({
            "cve_id": cve_id,
            "ground_truth_score": ground_truth['cvss_score'] if ground_truth else "Unknown",
            "ground_truth_severity": ground_truth['severity'] if ground_truth else "Unknown",
            "normal_rag_answer": rag_result['answer'],
            "rag_latency": rag_result['latency']
        })

    # 2. Save/Display Results
    results_df = pd.DataFrame(results)
    print("\n--- Evaluation Results ---")
    print(results_df[['cve_id', 'ground_truth_score', 'normal_rag_answer']])
    
    # Optional: Save to CSV for the report
    results_df.to_csv("evaluation_results_baseline.csv", index=False)
    print("\nResults saved to evaluation_results_baseline.csv")

if __name__ == "__main__":
    run_comparison()