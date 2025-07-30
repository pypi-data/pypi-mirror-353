"""
Differential privacy mechanisms.
"""

import random
from typing import Union, List


class LaplaceMechanism:
    """Laplace mechanism for differential privacy."""
    
    def __init__(self, epsilon: float, delta: float = 0.0):
        self.epsilon = epsilon
        self.delta = delta
    
    def apply(self, data: Union[float, List[float]], sensitivity: float = 1.0):
        """Apply Laplace noise."""
        scale = sensitivity / self.epsilon
        
        if isinstance(data, list):
            return [x + random.gauss(0, scale) for x in data]
        else:
            return data + random.gauss(0, scale)


class GaussianMechanism:
    """Gaussian mechanism for differential privacy."""
    
    def __init__(self, epsilon: float, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
    
    def apply(self, data: Union[float, List[float]], sensitivity: float = 1.0):
        """Apply Gaussian noise."""
        import math
        c = math.sqrt(2 * math.log(1.25 / self.delta))
        sigma = c * sensitivity / self.epsilon
        
        if isinstance(data, list):
            return [x + random.gauss(0, sigma) for x in data]
        else:
            return data + random.gauss(0, sigma)
