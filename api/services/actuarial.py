# services/actuarial.py
import math

def calculate_smart_rank_metrics(price_history, risk_aversion=0.5):
    """
    Calculates actuarial scoring for a given list of historical prices.
    """
    if not price_history or len(price_history) < 2:
        return {} # Not enough data

    n = len(price_history)
    expected_value = sum(price_history) / n
    
    # Calculate Variance and Standard Deviation
    variance = sum((p - expected_value) ** 2 for p in price_history) / (n - 1)
    std_dev = math.sqrt(variance)
    
    # Actuarial Formulas
    variance_penalty = (std_dev ** 2) * risk_aversion / 100
    risk_adjusted_score = expected_value - variance_penalty
    cv = std_dev / expected_value if expected_value else 0
    var_95 = expected_value - (1.645 * std_dev)
    
    return {
        'expected_value': round(expected_value, 2),
        'variance_penalty': round(variance_penalty, 2),
        'risk_adjusted_score': round(risk_adjusted_score, 2),
        'coefficient_of_variation': round(cv, 4),
        'var_95': round(var_95, 2)
    }