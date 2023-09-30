from chempy import BalancingError
from .gcd import float_gcd
from scipy.linalg import null_space
import numpy as np


def solve(system):
    results = null_space(system).T

    for result in results:
        if np.any(np.isclose(result, 0)):
            continue
        signs = result / np.abs(result)
        if np.allclose(signs, 1) or np.allclose(signs, -1):
            ratios = result * signs[0]
            break
    else:
        raise BalancingError('No solution found.', results)
    
    solution = ratios / float_gcd(ratios)
    
    if not np.allclose(solution, np.round(solution)):
        raise BalancingError(f'Unknown error.', results, ratios, solution)
    
    return np.round(solution).astype(int)
