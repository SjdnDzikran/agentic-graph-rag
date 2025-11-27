# src/evaluation_combined.py
import asyncio
import time
import pandas as pd
import random
import logging
import re
import math
from typing import List, Dict, Any
from google.api_core import exceptions as google_exceptions

# Import system components
# Pastikan Anda menjalankan ini dari root folder agar module 'src' terbaca
try:
    from src.graph.workflow import app as agentic_app
    from src.baselines.cvss_lookup import CVSSBaseline
except ImportError:
    print("❌ Error: Gagal mengimpor modul 'src'. Pastikan Anda menjalankan script dari root directory proyek.")
    exit(1)

# Suppress verbose logs
logging.getLogger("src.graph.workflow").setLevel(logging.ERROR)

# ==============================================================================
# BAGIAN 1: METRICS FUNCTIONS (Digabungkan dari src/utils/metrics.py)
# ==============================================================================

def get_severity_label(score: float) -> str:
    """Mengembalikan label severity berdasarkan skor CVSS v3.0/v3.1."""
    if score < 0.1: return "NONE"
    if score <= 3.9: return "LOW"
    if score <= 6.9: return "MEDIUM"
    if score <= 8.9: return "HIGH"
    return "CRITICAL"

def extract_score(text: str) -> float:
    """
    Mengekstrak angka floating point pertama yang menyerupai skor CVSS (0.0 - 10.0)
    dari teks.
    """
    # Regex untuk angka antara 0 dan 10
    match = re.search(r"\b(10(?:\.0)?|[0-9](?:\.[0-9])?)\b", text)
    if match:
        return float(match.group(0))
    return 0.0  # Default jika ekstraksi gagal

def calculate_spearman_rank_correlation(x: List[float], y: List[float]) -> float:
    """
    Menghitung korelasi Spearman's rho tanpa dependensi berat seperti scipy.
    """
    n = len(x)
    if n == 0: return 0.0
    
    # Helper untuk ranking
    def get_ranks(data):
        sorted_indices = sorted(range(len(data)), key=lambda k: data[k])
        ranks = [0] * len(data)
        for rank, index in enumerate(sorted_indices):
            ranks[index] = rank + 1
        return ranks

    rank_x = get_ranks(x)
    rank_y = get_ranks(y)
    
    d_squared_sum = sum((rx - ry) ** 2 for rx, ry in zip(rank_x, rank_y))
    
    # Rumus Spearman: 1 - (6 * sum(d^2)) / (n * (n^2 - 1))
    if n <= 1: return 0.0
    rho = 1 - (6 * d_squared_sum) / (n * (n**2 - 1))
    return rho

def calculate_classification_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
    """
    Menghitung Precision, Recall, dan Accuracy (Macro-averaged).
    """
    classes = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    metrics = {}
    
    # 1. Accuracy
    correct_predictions = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    metrics['accuracy'] = correct_predictions / len(y_true) if y_true else 0.0
    
    # 2. Macro-average Precision & Recall
    precisions = []
    recalls = []
    
    for cls in classes:
        # True Positives (TP)
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        # False Positives (FP)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != cls and p == cls)
        # False Negatives (FN)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p != cls)
        
        # Calculate per-class metrics
        p_score = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r_score = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        precisions.append(p_score)
        recalls.append(r_score)

    # Average across all classes (Macro)
    metrics['macro_precision'] = sum(precisions) / len(classes) if classes else 0.0
    metrics['macro_recall'] = sum(recalls) / len(classes) if classes else 0.0
    
    # F1 Score
    mp = metrics['macro_precision']
    mr = metrics['macro_recall']
    
    if (mp + mr) > 0:
        metrics['f1'] = 2 * (mp * mr) / (mp + mr)
    else:
        metrics['f1'] = 0.0
        
    return metrics

# ==============================================================================
# BAGIAN 2: LOGIKA EVALUASI UTAMA
# ==============================================================================

async def run_with_retry(func, *args, retries=5, delay=10):
    """
    Menjalankan fungsi dengan mekanisme retry untuk menangani limit kuota API.
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
                wait_time = delay * (2 ** i) # Exponential backoff
                print(f"\n[!] Kena Limit (Quota Exceeded). Menunggu {wait_time} detik sebelum coba lagi...")
                await asyncio.sleep(wait_time)
            else:
                raise e
    return "Error: Failed after max retries"

async def get_agentic_response(question: str):
    """Helper to invoke the Agentic Graph RAG"""
    inputs = {"question": question, "original_question": question}
    config = {"recursion_limit": 10}
    
    try:
        # Panggil ainvoke dengan retry handling
        result = await agentic_app.ainvoke(inputs, config=config)
        return result.get('answer', "No answer generated.")
    except Exception as e:
        return f"Error: {str(e)}"

async def run_experiments():
    # 1. Setup Data
    try:
        cvss_lookup = CVSSBaseline()
    except Exception as e:
        print(f"❌ Gagal memuat CVSSBaseline: {e}")
        return
    
    if cvss_lookup.df.empty:
        print("❌ Dataset kosong atau tidak ditemukan. Pastikan data/cve_dataset.csv ada.")
        return

    all_ids = cvss_lookup.df['id'].tolist()
    
    # SETUP SAMPLE: Ubah angka 5 menjadi jumlah sampel yang diinginkan
    sample_size = min(5, len(all_ids))
    test_cves = random.sample(all_ids, sample_size) 
    
    results = []
    print(f"--- Starting Evaluation on {len(test_cves)} CVEs (Agentic Only) ---")

    for cve_id in test_cves:
        print(f"\n[Eval] Processing {cve_id}...")
        
        # A. Ground Truth (Traditional CVSS / Baseline)
        gt_data = cvss_lookup.get_vulnerability_details(cve_id)
        if not gt_data: 
            print(f"   Skip {cve_id} (No Ground Truth)")
            continue
            
        # Ensure Score is float and Severity matches the prediction format
        gt_score = float(gt_data['cvss_score']) if gt_data.get('cvss_score') and gt_data['cvss_score'] != 'N/A' else 0.0
        gt_severity = get_severity_label(gt_score) # Hitung ulang label agar konsisten

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
            "agentic_raw_answer": agent_text[:100].replace('\n', ' ') + "..." 
        })

    # 2. Calculate Aggregate Metrics
    if not results:
        print("No results collected.")
        return

    df = pd.DataFrame(results)
    
    # Ranking Correlation (Spearman)
    rho_agentic = calculate_spearman_rank_correlation(df['gt_score'].tolist(), df['agentic_score'].tolist())
    
    # Classification Metrics
    metrics_agentic = calculate_classification_metrics(df['gt_severity'].tolist(), df['agentic_severity'].tolist())

    # 3. Display Final Report
    print("\n\n" + "="*40)
    print("       EXPERIMENTAL RESULTS (AGENTIC ONLY)       ")
    print("="*40)
    
    print(f"\n1. Ranking Correlation (Spearman's Rho):")
    print(f"   - Agentic RAG: {rho_agentic:.4f} (Target: mendekati 1.0)")
    
    print(f"\n2. Accuracy Metrics (Severity Classification):")
    print(f"   - Accuracy:    {metrics_agentic.get('accuracy', 0):.2f}")
    print(f"   - Precision:   {metrics_agentic.get('macro_precision', 0):.2f}")
    print(f"   - Recall:      {metrics_agentic.get('macro_recall', 0):.2f}")
    print(f"   - F1 Score:    {metrics_agentic.get('f1', 0):.2f}")
    
    print(f"\n3. Average Response Time (Latency):")
    print(f"   - Agentic RAG: {df['agentic_time'].mean():.2f} seconds")
    
    # Save detailed CSV
    output_filename = "evaluation_results_combined.csv"
    df.to_csv(output_filename, index=False)
    print(f"\nDetailed results saved to '{output_filename}'")

if __name__ == "__main__":
    asyncio.run(run_experiments())