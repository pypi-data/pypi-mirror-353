"""
ALU Math Vanguard - Group 15 Matrix Multiplication Library
A fun and educational matrix multiplication library with personality!

Authors:
- Cedric Izabayo
- Edith Nyanjiru Githinji
- Ntwali Eliel  
- Samuel Gakuru Wanjohi

Version: 1.0.0
"""

from .matrix_ops import MatrixMultiplier, Matrix, multiply_matrices, create_matrix, MatrixMultiplicationError

__version__ = "1.0.0"
__author__ = "ALU Math Vanguard Group 15"

# Make key classes available at package level
__all__ = ['MatrixMultiplier', 'Matrix', 'multiply_matrices', 'create_matrix', 'MatrixMultiplicationError']
