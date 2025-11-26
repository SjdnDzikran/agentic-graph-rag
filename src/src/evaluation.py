# src/evaluation.py
import pandas as pd
from src.baselines.cvss_lookup import CVSSBaseline

def get_severity_label(score: float) -> str:
    if score < 0.1: return "NONE"
    if score <= 3.9: return "LOW"
    if score <= 6.9: return "MEDIUM"
    if score <= 8.9: return "HIGH"
    return "CRITICAL"

def run_comparison():
    # Initialize lookup first to access the dataframe
    cvss_lookup = CVSSBaseline()
    
    # 1. Define Test Cases (CVE IDs to query)
    # Randomly select 10 CVE IDs from the dataset if available
    if not cvss_lookup.df.empty:
        sample_n = min(10, len(cvss_lookup.df))
        test_cves = cvss_lookup.df['id'].sample(n=sample_n).tolist()
    else:
        # Fallback if dataset is missing
        test_cves = ["CVE-2014-3566", "CVE-2015-7548", "CVE-2002-0059"]
    
    results = []

    print("--- Starting Comparison Framework (No RAG) ---")

    for cve_id in test_cves:
        print(f"\nProcessing {cve_id}...")
        
        # A. Ground Truth (CVSS Baseline)
        ground_truth = cvss_lookup.get_vulnerability_details(cve_id)

        if ground_truth:
            raw_score = ground_truth.get("cvss_score")
            
            # Handle NaN, 'N/A', or missing values by setting them to 0.0
            try:
                if pd.isna(raw_score) or raw_score == 'N/A' or raw_score == '':
                    score = 0.0
                else:
                    score = float(raw_score)
            except (ValueError, TypeError):
                score = 0.0
                
            severity = get_severity_label(score)
        else:
            score = 0.0
            severity = "Unknown"

        # B. Store results
        results.append({
            "cve_id": cve_id,
            "cvss_score": score,
            "severity_calculated": severity,
            "severity_from_database": ground_truth.get("severity") if ground_truth else "Unknown"
        })

    # 2. Create DataFrame & show results
    results_df = pd.DataFrame(results)

    print("\n--- Evaluation Results ---")
    print(results_df[['cve_id', 'cvss_score', 'severity_calculated']])

    # Save as CSV
    results_df.to_csv("evaluation_results_baseline_only.csv", index=False)
    print("\nResults saved to evaluation_results_baseline_only.csv")

if __name__ == "__main__":
    run_comparison()