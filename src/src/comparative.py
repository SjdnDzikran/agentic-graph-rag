# src/evaluation3.py
import asyncio
import time
import pandas as pd
import random
import logging
from google.api_core import exceptions as google_exceptions

# Import system components
from src.graph.workflow import app as agentic_app
from src.baselines.cvss_lookup import CVSSBaseline
from src.utils.metrics import (
    extract_score, 
    get_severity_label, 
    calculate_spearman_rank_correlation, 
    calculate_classification_metrics
)

# Suppress verbose logs
logging.getLogger("src.graph.workflow").setLevel(logging.ERROR)

# --- FUNGSI RETRY OTOMATIS (FIX LIMIT) ---
async def run_with_retry(func, *args, retries=5, delay=10):
    """
    Menjalankan fungsi (sync atau async) dengan mekanisme retry 
    jika terkena limit kuota Gemini.
    """
    for i in range(retries):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args)
            else:
                return func(*args)
        except Exception as e:
            error_msg = str(e).lower()
            # Cek error 429 atau Quota exceeded
            if "429" in error_msg or "quota" in error_msg or "resourceexhausted" in error_msg:
                wait_time = delay * (2 ** i) # Exponential backoff (10s, 20s, 40s...)
                print(f"\n[!] Kena Limit (Quota Exceeded). Menunggu {wait_time} detik sebelum coba lagi...")
                await asyncio.sleep(wait_time)
            else:
                # Jika error lain, jangan retry
                raise e
    return "Error: Failed after max retries"

async def get_agentic_response(question: str):
    """Helper to invoke the Agentic Graph RAG"""
    inputs = {"question": question, "original_question": question}
    config = {"recursion_limit": 10} # Limit rekursi untuk workflow yang kompleks
    
    try:
        # Panggil ainvoke dengan retry handling
        result = await agentic_app.ainvoke(inputs, config=config)
        return result.get('answer', "No answer generated.")
    except Exception as e:
        return f"Error: {str(e)}"

async def run_experiments():
    # 1. Setup Data
    cvss_lookup = CVSSBaseline()
    
    # Ambil sample CVE
    if cvss_lookup.df.empty:
        print("❌ Dataset kosong atau tidak ditemukan. Pastikan data/cve_dataset.csv ada.")
        return

    all_ids = cvss_lookup.df['id'].tolist()
    # Gunakan sample kecil (misal 5) untuk tes cepat, atau lebih banyak untuk hasil akurat
    test_cves = random.sample(all_ids, min(5, len(all_ids))) 
    
    results = []
    print(f"--- Starting Evaluation on {len(test_cves)} CVEs (Agentic Only) ---")

    for cve_id in test_cves:
        print(f"\n[Eval] Processing {cve_id}...")
        
        # A. Ground Truth (Traditional CVSS / Baseline)
        gt_data = cvss_lookup.get_vulnerability_details(cve_id)
        if not gt_data: 
            print(f"   Skip {cve_id} (No Ground Truth)")
            continue
            
        # FIX: Ensure Score is float and Severity matches the prediction format (UPPERCASE)
        gt_score = float(gt_data['cvss_score']) if gt_data['cvss_score'] != 'N/A' else 0.0
        
        # --- PERBAIKAN DI SINI ---
        # Jangan ambil teks mentah dari CSV (karena mungkin 'N/A' atau 'High').
        # Hitung label dari skor agar formatnya sama dengan prediksi (LOW/MEDIUM/HIGH/CRITICAL).
        gt_severity = get_severity_label(gt_score)

        query = f"What is the CVSS score and severity for {cve_id}?"

        # B. Agentic RAG (The 'Fork' Agent)
        print("   Running Agentic RAG...", end="", flush=True)
        start_agent = time.time()
        agent_text = await run_with_retry(get_agentic_response, query)
        agent_time = time.time() - start_agent
        print(" Done.")
        
        # C. Extraction & Metrics
        agent_score_pred = extract_score(agent_text)
        agent_severity_pred = get_severity_label(agent_score_pred)

        results.append({
            "cve_id": cve_id,
            "gt_score": gt_score,
            "gt_severity": gt_severity,
            # Agentic RAG Results
            "agentic_score": agent_score_pred,
            "agentic_severity": agent_severity_pred,
            "agentic_time": agent_time,
            "agentic_raw_answer": agent_text[:100] + "..." 
        })

        # --- COOLING DOWN ---
        # Jeda untuk menghindari rate limit API
        print("   Cooling down for 5s...")
        await asyncio.sleep(5)

    # 2. Calculate Aggregate Metrics
    if not results:
        print("No results collected.")
        return

    df = pd.DataFrame(results)
    
    # Ranking Correlation (Spearman) - Hanya untuk Agentic
    rho_agentic = calculate_spearman_rank_correlation(df['gt_score'].tolist(), df['agentic_score'].tolist())
    
    # Classification Metrics - Hanya untuk Agentic
    metrics_agentic = calculate_classification_metrics(df['gt_severity'].tolist(), df['agentic_severity'].tolist())

    # 3. Display Final Report
    print("\n\n" + "="*40)
    print("       EXPERIMENTAL RESULTS (AGENTIC ONLY)       ")
    print("="*40)
    
    print(f"\n1. Ranking Correlation (Spearman's Rho):")
    print(f"   - Agentic RAG: {rho_agentic:.4f} (Target: mendekati 1.0)")
    
    print(f"\n2. Accuracy Metrics (Severity Classification):")
    print(f"   - Accuracy:  {metrics_agentic.get('accuracy', 0):.2f}")
    print(f"   - Precision: {metrics_agentic.get('macro_precision', 0):.2f}")
    print(f"   - Recall:    {metrics_agentic.get('macro_recall', 0):.2f}")
    print(f"   - F1 Score:  {metrics_agentic.get('f1', 0):.2f}")
    
    print(f"\n3. Average Response Time (Latency):")
    print(f"   - Agentic RAG: {df['agentic_time'].mean():.2f} seconds")
    
    # Save detailed CSV
    df.to_csv("evaluation_results.csv", index=False)
    print(f"\nDetailed results saved to 'evaluation_results.csv'")

if __name__ == "__main__":
    asyncio.run(run_experiments())