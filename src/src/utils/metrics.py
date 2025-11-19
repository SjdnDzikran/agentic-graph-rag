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

def calculate_classification_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, float]:
    """
    Calculates simplified Precision, Recall, and Accuracy for severity labels.
    Macro-averaged over classes.
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
        # True Positives (TP): Predicted cls AND True cls
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        
        # False Positives (FP): Predicted cls BUT True is NOT cls
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != cls and p == cls)
        
        # False Negatives (FN): True is cls BUT Predicted NOT cls
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p != cls)
        
        # Calculate per-class metrics
        p_score = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r_score = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        precisions.append(p_score)
        recalls.append(r_score)

    # Average across all classes
    metrics['precision'] = sum(precisions) / len(classes) if classes else 0.0
    metrics['recall'] = sum(recalls) / len(classes) if classes else 0.0
    
    # F1 Score (Harmonic mean of macro-precision and macro-recall)
    if (metrics['precision'] + metrics['recall']) > 0:
        metrics['f1'] = 2 * (metrics['precision'] * metrics['recall']) / (metrics['precision'] + metrics['recall'])
    else:
        metrics['f1'] = 0.0
        
    return metrics