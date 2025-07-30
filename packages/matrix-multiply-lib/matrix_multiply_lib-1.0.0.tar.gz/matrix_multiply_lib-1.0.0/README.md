# Matrix Multiply Library

A Python library for matrix multiplication supporting matrices of different dimensions.

## Installation

```bash
pip install matrix-multiply-lib
```
##Usage
```bash
from matrix_multiply import Matrix, matrix_multiply

# Create matrices
matrix_a = Matrix([[1, 2], [3, 4]])
matrix_b = Matrix([[5, 6], [7, 8]])

# Method 1: Using Matrix class
result = matrix_a * matrix_b
print(result)

# Method 2: Using convenience function
result = matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
print(result)