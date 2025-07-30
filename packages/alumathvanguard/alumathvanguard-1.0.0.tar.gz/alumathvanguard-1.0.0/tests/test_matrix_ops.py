"""
Test suite for ALU Math Vanguard matrix multiplication library
"""

import unittest
import alumathvanguard as amv


class TestMatrix(unittest.TestCase):
    """Test the Matrix class"""
    
    def test_matrix_creation(self):
        """Test basic matrix creation"""
        data = [[1, 2], [3, 4]]
        matrix = amv.Matrix(data)
        self.assertEqual(matrix.rows, 2)
        self.assertEqual(matrix.cols, 2)
        self.assertEqual(matrix.data, data)
    
    def test_matrix_dimensions(self):
        """Test matrix dimension reporting"""
        matrix = amv.Matrix([[1, 2, 3], [4, 5, 6]])
        self.assertEqual(matrix.get_dimensions(), (2, 3))
    
    def test_matrix_string_representation(self):
        """Test matrix string representation"""
        matrix = amv.Matrix([[1, 2], [3, 4]])
        str_repr = str(matrix)
        self.assertIn("1.00", str_repr)
        self.assertIn("2.00", str_repr)
    
    def test_empty_matrix_error(self):
        """Test that empty matrices raise errors"""
        with self.assertRaises(ValueError):
            amv.Matrix([])
        
        with self.assertRaises(ValueError):
            amv.Matrix([[]])
    
    def test_inconsistent_row_length_error(self):
        """Test that matrices with inconsistent row lengths raise errors"""
        with self.assertRaises(ValueError):
            amv.Matrix([[1, 2], [3, 4, 5]])


class TestMatrixMultiplier(unittest.TestCase):
    """Test the MatrixMultiplier class"""
    
    def test_basic_multiplication(self):
        """Test basic 2x2 matrix multiplication"""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        
        result = amv.MatrixMultiplier.multiply(A, B)
        
        # Expected result: [[19, 22], [43, 50]]
        expected = [[19, 22], [43, 50]]
        self.assertEqual(result.data, expected)
        self.assertEqual(result.get_dimensions(), (2, 2))
    
    def test_different_dimensions(self):
        """Test multiplication with different dimensions"""
        A = [[1, 2, 3], [4, 5, 6]]  # 2x3
        B = [[7, 8], [9, 10], [11, 12]]  # 3x2
        
        result = amv.MatrixMultiplier.multiply(A, B)
        
        # Expected result: [[58, 64], [139, 154]]
        expected = [[58, 64], [139, 154]]
        self.assertEqual(result.data, expected)
        self.assertEqual(result.get_dimensions(), (2, 2))
    
    def test_incompatible_dimensions(self):
        """Test that incompatible matrices raise errors"""
        A = [[1, 2, 3], [4, 5, 6]]  # 2x3
        B = [[7, 8], [9, 10]]       # 2x2
        
        with self.assertRaises(Exception) as context:
            amv.MatrixMultiplier.multiply(A, B)
        
        # Check that the error message contains one of our team members' names
        error_message = str(context.exception)
        team_members = ["Cedric", "Edith", "Ntwali", "Samuel"]
        self.assertTrue(any(member in error_message for member in team_members))
    
    def test_can_multiply(self):
        """Test the can_multiply method"""
        A = [[1, 2], [3, 4]]
        B = [[5, 6], [7, 8]]
        self.assertTrue(amv.MatrixMultiplier.can_multiply(A, B))
        
        C = [[1, 2, 3]]
        D = [[1, 2], [3, 4]]
        self.assertFalse(amv.MatrixMultiplier.can_multiply(C, D))
    
    def test_get_result_dimensions(self):
        """Test getting result dimensions"""
        A = [[1, 2, 3], [4, 5, 6]]  # 2x3
        B = [[7, 8], [9, 10], [11, 12]]  # 3x2
        
        dims = amv.MatrixMultiplier.get_result_dimensions(A, B)
        self.assertEqual(dims, (2, 2))
        
        # Test with incompatible matrices
        C = [[1, 2, 3]]  # 1x3
        D = [[1, 2], [3, 4]]  # 2x2
        
        with self.assertRaises(Exception):
            amv.MatrixMultiplier.get_result_dimensions(C, D)
    
    def test_matrix_object_input(self):
        """Test that Matrix objects work as input"""
        A = amv.Matrix([[1, 2], [3, 4]])
        B = amv.Matrix([[5, 6], [7, 8]])
        
        result = amv.MatrixMultiplier.multiply(A, B)
        expected = [[19, 22], [43, 50]]
        self.assertEqual(result.data, expected)


if __name__ == '__main__':
    unittest.main()
