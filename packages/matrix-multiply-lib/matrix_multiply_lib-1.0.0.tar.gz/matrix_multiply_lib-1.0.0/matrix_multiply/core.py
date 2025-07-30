class Matrix:
    def __init__(self, data):
        """Initialize matrix with 2D list of numbers"""
        if not isinstance(data, list) or not all(isinstance(row, list) for row in data):
            raise ValueError("Matrix data must be a 2D list")
        
        if not data or not data[0]:
            raise ValueError("Matrix cannot be empty")
        
        row_length = len(data[0])
        if not all(len(row) == row_length for row in data):
            raise ValueError("All rows must have the same length")
        
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0])
    
    def multiply(self, other):
        """Multiply this matrix with another matrix"""
        if not isinstance(other, Matrix):
            raise TypeError("Can only multiply with another Matrix")
        
        if self.cols != other.rows:
            raise ValueError(f"Cannot multiply {self.rows}x{self.cols} matrix with {other.rows}x{other.cols} matrix")
        
        # Initialize result matrix with zeros
        result = [[0 for _ in range(other.cols)] for _ in range(self.rows)]
        
        # Perform matrix multiplication
        for i in range(self.rows):
            for j in range(other.cols):
                for k in range(self.cols):
                    result[i][j] += self.data[i][k] * other.data[k][j]
        
        return Matrix(result)
    
    def __mul__(self, other):
        """Allow using * operator for multiplication"""
        return self.multiply(other)
    
    def __str__(self):
        return '\n'.join([' '.join(map(str, row)) for row in self.data])
    
    def __repr__(self):
        return f"Matrix({self.data})"

def matrix_multiply(matrix_a, matrix_b):
    """Convenience function for matrix multiplication"""
    if isinstance(matrix_a, list):
        matrix_a = Matrix(matrix_a)
    if isinstance(matrix_b, list):
        matrix_b = Matrix(matrix_b)
    
    return matrix_a.multiply(matrix_b)