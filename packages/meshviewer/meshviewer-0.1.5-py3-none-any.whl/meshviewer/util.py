"""
Utility functions for meshviewer
"""
import numpy as np

def allclose(a, b, atol=1e-8):
    """
    Replacement for trimesh.util.allclose that works with NumPy 2.0+
    
    Parameters
    ----------
    a : array_like
        First array to compare
    b : array_like
        Second array to compare
    atol : float
        Absolute tolerance
        
    Returns
    -------
    bool
        True if arrays are close
    """
    return float(np.ptp(a - b)) < atol