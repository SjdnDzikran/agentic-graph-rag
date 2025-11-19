# src/utils/metrics.py
import re
from typing import List, Dict, Any
import math

# Standard CVSS v3.0/v3.1 Severity Ratings
def get_severity_label(score: float) -> str:
    if score < 0.1: return "NONE"
    if score <= 3.9: return "LOW"
    if score <= 6.9: return "MEDIUM"
    if score <= 8.9: return "HIGH"
    return "CRITICAL"

def extract_score(text: str) -> float:
    """
    Extracts the first floating point number looking like a CVSS score (0.0 - 10.0)
    from the text.
    """
    # Regex for number between 0 and 10
    match = re.search(r"\b(10(?:\.0)?|[0-9](?:\.[0-9])?)\b", text)
    if match:
        return float(match.group(0))
    return 0.0  # Default if extraction fails

def calculate_spearman_rank_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculates Spearman's rho without external heavy dependencies like scipy/pandas 
    to ensure it runs in your minimal environment.
    """
    n = len(x)
    if n == 0: return 0.0
    
    # Rank helper
    def get_ranks(data):
        sorted_indices = sorted(range(len(data)), key=lambda k: data[k])
        ranks = [0] * len(data)
        for rank, index in enumerate(sorted_indices):
            ranks[index] = rank + 1
        return ranks

    rank_x = get_ranks(x)
    rank_y = get_ranks(y)
    
    d_squared_sum = sum((rx - ry) ** 2 for rx, ry in zip(rank_x, rank_y))
    
    # Spearman formula: 1 - (6 * sum(d^2)) / (n * (n^2 - 1))
    if n <= 1: return 0.0
    rho = 1 - (6 * d_squared_sum) / (n * (n**2 - 1))
    return rho

def calculate_classification_metrics(y_true: List[str], y_pred: List[str]):
    """
    Calculates simplified Precision, Recall, and Accuracy for severity labels.
    """
    classes = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    metrics = {}
    
    correct_predictions = 0
    for t, p in zip(y_true, y_pred):
        if t == p:
            correct_predictions += 1
            
    metrics['accuracy'] = correct_predictions / len(y_true) if y_true else 0
    
    # Macro-average Precision/Recall
    precisions = []
    recalls = []
    
    for cls in classes:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        fp