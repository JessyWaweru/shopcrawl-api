# services/actuarial.py
import math

def calculate_actuarial_metrics(prices, risk_aversion=0.5):
    """
    Calculates the actuarial SmartRank™ metrics for a given list of prices.
    Ignores None or zero values.
    """
    # Filter out None and 0/negative prices
    valid_prices = [float(p) for p in prices if p is not None and float(p) > 0]
    
    if not valid_prices:
        return {
            'expected_value': 0.0,
            'variance_penalty': 0.0,
            'risk_adjusted_score': 0.0,
            'coefficient_of_variation': 0.0,
            'var_95': 0.0
        }

    n = len(valid_prices)
    expected_value = sum(valid_prices) / n
    
    if n < 2:
        # Not enough data for volatility metrics. Return baseline values.
        return {
            'expected_value': round(expected_value, 2),
            'variance_penalty': 0.0,
            'risk_adjusted_score': round(expected_value, 2),
            'coefficient_of_variation': 0.0,
            'var_95': round(expected_value, 2)
        }

    # Calculate Sample Variance and Standard Deviation
    variance = sum((p - expected_value) ** 2 for p in valid_prices) / (n - 1)
    std_dev = math.sqrt(variance)
    
    # --- ACTUARIAL FORMULAS ---
    
    # 1. Variance Penalty: (StdDev^2) * lambda / 100
    variance_penalty = (std_dev ** 2) * risk_aversion / 100
    
    # 2. Risk-Adjusted Score: Expected Value minus the risk penalty
    risk_adjusted_score = expected_value - variance_penalty
    
    # 3. Coefficient of Variation (CV): StdDev / Mean (Measure of relative volatility)
    cv = std_dev / expected_value if expected_value else 0.0
    
    # 4. Value-at-Risk (VaR) at 95% confidence: Mean - 1.645(StdDev)
    var_95 = expected_value - (1.645 * std_dev)
    
    return {
        'expected_value': round(expected_value, 2),
        'variance_penalty': round(variance_penalty, 2),
        'risk_adjusted_score': round(risk_adjusted_score, 2),
        'coefficient_of_variation': round(cv, 4),
        'var_95': round(var_95, 2)
    }

def update_product_actuarial_data(product_instance):
    """
    Helper function to extract cross-vendor prices from a Product,
    calculate the SmartRank metrics, and save them to the database.
    """
    # Extract prices from existing vendors
    prices = []
    if product_instance.amazon and product_instance.amazon.price:
        prices.append(product_instance.amazon.price)
    if product_instance.jumia and product_instance.jumia.price:
        prices.append(product_instance.jumia.price)
    if product_instance.kilimall and product_instance.kilimall.price:
        prices.append(product_instance.kilimall.price)
    if product_instance.shopify and product_instance.shopify.price:
        prices.append(product_instance.shopify.price)
        
    # Calculate metrics
    metrics = calculate_actuarial_metrics(prices)
    
    # Update Product model
    product_instance.expected_value = metrics['expected_value']
    product_instance.variance_penalty = metrics['variance_penalty']
    product_instance.risk_adjusted_score = metrics['risk_adjusted_score']
    product_instance.var_95 = metrics['var_95']
    
    # Save the updated actuarial data
    product_instance.save(update_fields=[
        'expected_value', 
        'variance_penalty', 
        'risk_adjusted_score', 
        'var_95'
    ])
    
    return product_instance