from datetime import timedelta
import math

def forecast_sales_moving_average(daily_sales, days_to_predict=7, window_size=7):
    """
    Predicts future sales using a simple moving average.
    daily_sales: list of dicts [{'date': date_obj, 'revenue': float}] sorted chronologically.
    Returns: list of dicts [{'date': date_obj, 'predicted_revenue': float}]
    """
    if not daily_sales:
        return []
        
    predictions = []
    revenues = [s['revenue'] for s in daily_sales]
    
    last_date = daily_sales[-1]['date']
    
    for i in range(days_to_predict):
        # Calculate moving average of the last `window_size` days
        current_window = revenues[-window_size:] if len(revenues) >= window_size else revenues
        next_val = sum(current_window) / len(current_window) if current_window else 0
        
        revenues.append(next_val)
        next_date = last_date + timedelta(days=i+1)
        
        predictions.append({
            'date': next_date,
            'predicted_revenue': round(next_val, 2)
        })
        
    return predictions

def linear_regression_trend(daily_sales):
    """
    Calculates the linear regression trend (slope and intercept) for sales.
    Returns a dict with slope, intercept, and a trend indication ('increasing', 'decreasing', 'flat')
    """
    if len(daily_sales) < 2:
        return {'slope': 0, 'intercept': 0, 'trend': 'flat'}
        
    # X = days from start, Y = revenue
    n = len(daily_sales)
    sum_x = sum(range(n))
    sum_y = sum(s['revenue'] for s in daily_sales)
    
    sum_xy = sum(i * s['revenue'] for i, s in enumerate(daily_sales))
    sum_xx = sum(i * i for i in range(n))
    
    denominator = (n * sum_xx - sum_x * sum_x)
    if denominator == 0:
        return {'slope': 0, 'intercept': sum_y / n if n > 0 else 0, 'trend': 'flat'}
        
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    trend_type = 'increasing' if slope > 0.1 else ('decreasing' if slope < -0.1 else 'flat')
    
    return {
        'slope': round(slope, 4),
        'intercept': round(intercept, 4),
        'trend': trend_type
    }

def get_product_recommendations(user_sales_qs, all_sales_qs):
    """
    Very basic recommendation engine.
    Finds products the user hasn't bought that are popular overall,
    or suggests reordering their most frequently bought item if it's been a while.
    """
    if not user_sales_qs.exists():
        # Recommend overall top products
        top_products = list(all_sales_qs.values_list('product__name', flat=True))
        from collections import Counter
        most_common = Counter(top_products).most_common(3)
        return [
            {'product': name, 'reason': 'Consistently popular across all customer segments'} 
            for name, count in most_common if name
        ]
        
    # User's top bought products
    user_products = list(user_sales_qs.values_list('product__name', flat=True))
    from collections import Counter
    user_counts = Counter(user_products)
    user_top = [name for name, count in user_counts.most_common() if name]
    
    recommendations = []
    if user_top:
        recommendations.append({
            'product': user_top[0],
            'reason': 'High reorder potential based on recent purchase frequency'
        })
        
    # Overall top products not in user's top
    all_products = list(all_sales_qs.values_list('product__name', flat=True))
    all_counts = Counter(all_products)
    
    for name, count in all_counts.most_common():
        if name and name not in user_top:
            recommendations.append({
                'product': name,
                'reason': 'Trending product with rising customer interest'
            })
            if len(recommendations) >= 3:
                break
                
    return recommendations
