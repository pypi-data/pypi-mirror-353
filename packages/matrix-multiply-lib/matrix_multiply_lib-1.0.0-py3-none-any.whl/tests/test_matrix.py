## Step 6: Create Tests


import unittest
from matrix_multiply import Matrix, matrix_multiply

class TestMatrixMultiply(unittest.TestCase):
    
    def test_basic_multiplication(self):
        """Test basic 2x2 matrix multiplication"""
        a = Matrix([[1, 2], [3, 4]])
        b = Matrix([[5, 6], [7, 8]])
        result = a * b
        expected = Matrix([[19, 22], [43, 50]])
        self.assertEqual(result.data, expected.data)
    
    def test_different_dimensions(self):
        """Test multiplication with different compatible dimensions"""
        a = Matrix([[1, 2, 3]])  # 1x3
        b = Matrix([[4], [5], [6]])  # 3x1
        result = a * b
        expected = Matrix([[32]])  # 1x1
        self.assertEqual(result.data, expected.data)
    
    def test_incompatible_dimensions(self):
        """Test error handling for incompatible dimensions"""
        a = Matrix([[1, 2]])  # 1x2
        b = Matrix([[3, 4, 5]])  # 1x3
        with self.assertRaises(ValueError):
            a * b
    
    def test_convenience_function(self):
        """Test the convenience function"""
        result = matrix_multiply([[1, 2]], [[3], [4]])
        expected_data = [[11]]
        self.assertEqual(result.data, expected_data)

if __name__ == '__main__':
    unittest.main()