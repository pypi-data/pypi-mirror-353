"""
Differential privacy demonstration with Themis.
"""

import numpy as np
from themis.core.differential_privacy import (
    LaplaceMechanism, 
    GaussianMechanism,
    PrivateAggregator,
    PrivacyAccountant
)

def main():
    """Demonstrate differential privacy mechanisms."""
    
    print("Themis Differential Privacy Demo")
    print("=" * 40)
    
    # Sample sensitive data (e.g., user ratings)
    sensitive_data = [4.2, 3.8, 4.5, 3.9, 4.1, 3.7, 4.3, 4.0, 3.6, 4.4]
    print(f"Original data: {sensitive_data}")
    print(f"True mean: {np.mean(sensitive_data):.3f}")
    
    # Privacy parameters
    epsilon = 1.0
    delta = 1e-5
    
    print(f"\nPrivacy parameters: ε={epsilon}, δ={delta}")
    print("-" * 40)
    
    # 1. Laplace Mechanism
    print("\n1. Laplace Mechanism")
    laplace_mech = LaplaceMechanism(epsilon=epsilon)
    
    # Apply to individual values
    private_values = laplace_mech.apply(sensitive_data, sensitivity=1.0)
    print(f"Private values: {[round(v, 3) for v in private_values]}")
    print(f"Private mean: {np.mean(private_values):.3f}")
    print(f"Error: {abs(np.mean(private_values) - np.mean(sensitive_data)):.3f}")
    
    # 2. Gaussian Mechanism
    print("\n2. Gaussian Mechanism")
    gaussian_mech = GaussianMechanism(epsilon=epsilon, delta=delta)
    
    private_mean = gaussian_mech.apply(np.mean(sensitive_data), sensitivity=0.1)
    print(f"Private mean (Gaussian): {private_mean:.3f}")
    print(f"Error: {abs(private_mean - np.mean(sensitive_data)):.3f}")
    
    # 3. Private Aggregation
    print("\n3. Private Aggregation")
    aggregator = PrivateAggregator(LaplaceMechanism(epsilon=0.5))
    
    private_sum = aggregator.private_sum(sensitive_data, clipping_threshold=5.0)
    private_count = aggregator.private_count(sensitive_data)
    private_mean_agg = private_sum / private_count
    
    print(f"Private sum: {private_sum:.3f}")
    print(f"Private count: {private_count:.3f}")
    print(f"Private mean (aggregated): {private_mean_agg:.3f}")
    
    # 4. Privacy Accounting
    print("\n4. Privacy Accounting")
    accountant = PrivacyAccountant(total_epsilon=2.0, total_delta=1e-4)
    
    # Simulate multiple queries
    try:
        accountant.charge(0.5, 0, "laplace", "mean_query")
        accountant.charge(0.3, 1e-5, "gaussian", "sum_query")
        accountant.charge(0.2, 0, "laplace", "count_query")
        
        print("Privacy budget usage:")
        report = accountant.get_privacy_report()
        print(f"Used epsilon: {report['used_budget']['epsilon']:.3f}")
        print(f"Used delta: {report['used_budget']['delta']:.2e}")
        print(f"Remaining epsilon: {report['remaining_budget']['epsilon']:.3f}")
        print(f"Queries executed: {report['queries_executed']}")
        
    except RuntimeError as e:
        print(f"Privacy budget error: {e}")
    
    # 5. Histogram with Privacy
    print("\n5. Private Histogram")
    
    # Create categorical data
    categories = ['A', 'B', 'C', 'A', 'B', 'A', 'C', 'A', 'B', 'C']
    bins = ['A', 'B', 'C']
    
    histogram_aggregator = PrivateAggregator(LaplaceMechanism(epsilon=0.5))
    private_hist = histogram_aggregator.private_histogram(categories, bins)
    
    print("Private histogram:")
    for category, count in private_hist.items():
        true_count = categories.count(category)
        print(f"{category}: {count:.1f} (true: {true_count})")
    
    # 6. Utility-Privacy Tradeoff Analysis
    print("\n6. Utility-Privacy Tradeoff")
    epsilon_values = [0.1, 0.5, 1.0, 2.0, 5.0]
    
    print("Epsilon\tPrivate Mean\tError")
    print("-" * 30)
    
    for eps in epsilon_values:
        mech = LaplaceMechanism(epsilon=eps)
        private_val = mech.apply(np.mean(sensitive_data), sensitivity=0.1)
        error = abs(private_val - np.mean(sensitive_data))
        print(f"{eps}\t{private_val:.3f}\t\t{error:.3f}")
    
    print("\nDifferential privacy demo complete!")
    print("Lower epsilon = more privacy, higher noise")
    print("Higher epsilon = less privacy, lower noise")


if __name__ == "__main__":
    main()