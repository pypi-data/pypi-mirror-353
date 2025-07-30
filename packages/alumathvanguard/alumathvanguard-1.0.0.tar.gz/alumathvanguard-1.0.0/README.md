# 🚀 ALU Math Vanguard - Group 15 Matrix Multiplier

A fun and educational Python library for matrix multiplication with personality! Created by Group 15 as part of our formative assessment.

## 👥 Team Members (ALU Math Vanguard - Group 15)

- **Edith Nyanjiru Githinji** (Group Leader) 👑
- **Cedric Izabayo** 💻
- **Ntwali Eliel** 🔢
- **Samuel Gakuru Wanjohi** ⚡

## 🎯 Features

- ✅ Easy matrix multiplication with intuitive API
- 😄 Funny, personalized error messages from each team member
- 🛡️ Robust dimension checking and validation
- 📚 Educational error messages that help you learn
- 🎲 Randomized error messages for entertainment
- 🔧 Support for both Matrix objects and raw 2D lists

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install alumathvanguard
```

### From Source

```bash
git clone https://github.com/izabayo7/Formative2Group15.git
cd Group15MatrixMultiplier/alumathvanguard
pip install -e .
```

## 🚀 Quick Start

```python
import alumathvanguard as amv

# Create matrices using 2D lists
matrix_a = [
    [1, 2, 3],
    [4, 5, 6]
]

matrix_b = [
    [7, 8],
    [9, 10],
    [11, 12]
]

# Method 1: Using the MatrixMultiplier class
result = amv.MatrixMultiplier.multiply(matrix_a, matrix_b)
print("Result:")
print(result)

# Method 2: Using convenience function
result2 = amv.multiply_matrices(matrix_a, matrix_b)
print("Same result with convenience function:")
print(result2)

# Method 3: Using Matrix objects directly
mat_a = amv.Matrix(matrix_a)
mat_b = amv.Matrix(matrix_b)
result3 = amv.MatrixMultiplier.multiply(mat_a, mat_b)
print("Result with Matrix objects:")
print(result3)
```

## 🎭 The Fun Part - Personalized Error Messages!

When you try to multiply incompatible matrices, each team member has their own style of telling you "No!":

```python
import alumathvanguard as amv

# This will trigger a funny error message!
try:
    incompatible_a = [[1, 2, 3], [4, 5, 6]]  # 2x3 matrix
    incompatible_b = [[1, 2], [3, 4]]        # 2x2 matrix (can't multiply 2x3 * 2x2)

    result = amv.MatrixMultiplier.multiply(incompatible_a, incompatible_b)
except amv.MatrixMultiplicationError as e:
    print(e)
    # You'll get a random funny message from one of our team members!
```

Sample error messages:

- **Cedric**: "Cedric can't allow you to do that because he's too busy debugging his own code to fix your matrix dimensions!"
- **Edith**: "Edith (the group leader) can't permit this because she has standards, and your matrices don't meet them!"
- **Ntwali**: "Ntwali can't allow this because he's too busy solving actual solvable problems!"
- **Samuel**: "Samuel can't let you do that because he's seen what happens when dimensions don't match - chaos!"

## 📖 Detailed Usage Examples

### Basic Matrix Multiplication

```python
import alumathvanguard as amv

# Example 1: 2x3 matrix * 3x2 matrix = 2x2 matrix
A = [
    [1, 2, 3],
    [4, 5, 6]
]

B = [
    [7, 8],
    [9, 10],
    [11, 12]
]

result = amv.MatrixMultiplier.multiply(A, B)
print(f"A ({len(A)}x{len(A[0])}) * B ({len(B)}x{len(B[0])}) = Result ({result.rows}x{result.cols})")
print(result)
```

### Checking Compatibility Before Multiplication

```python
import alumathvanguard as amv

A = [[1, 2], [3, 4]]
B = [[5, 6, 7], [8, 9, 10]]

# Check if matrices can be multiplied
if amv.MatrixMultiplier.can_multiply(A, B):
    result = amv.MatrixMultiplier.multiply(A, B)
    print("Multiplication successful!")
    print(result)
else:
    print("These matrices cannot be multiplied")

# Get result dimensions without actually computing
try:
    dims = amv.MatrixMultiplier.get_result_dimensions(A, B)
    print(f"Result would be {dims[0]}x{dims[1]} matrix")
except amv.MatrixMultiplicationError as e:
    print("Cannot multiply these matrices!")
```

### Working with Matrix Objects

```python
import alumathvanguard as amv

# Create Matrix objects
matrix1 = amv.Matrix([[1, 2], [3, 4], [5, 6]])  # 3x2
matrix2 = amv.Matrix([[7, 8, 9], [10, 11, 12]]) # 2x3

print(f"Matrix 1: {matrix1.get_dimensions()}")
print(matrix1)
print(f"\nMatrix 2: {matrix2.get_dimensions()}")
print(matrix2)

# Multiply them
result = amv.MatrixMultiplier.multiply(matrix1, matrix2)
print(f"\nResult: {result.get_dimensions()}")
print(result)
```

## 🔧 API Reference

### Classes

#### `Matrix`

Represents a mathematical matrix with validation and display features.

**Constructor:**

- `Matrix(data: List[List[Union[int, float]]])` - Create matrix from 2D list

**Methods:**

- `get_dimensions()` - Returns (rows, cols) tuple
- `__str__()` - Pretty string representation
- `__repr__()` - Object representation

**Properties:**

- `data` - The underlying 2D list
- `rows` - Number of rows
- `cols` - Number of columns

#### `MatrixMultiplier`

Static class for matrix multiplication operations.

**Methods:**

- `multiply(matrix1, matrix2)` - Multiply two matrices
- `can_multiply(matrix1, matrix2)` - Check if matrices can be multiplied
- `get_result_dimensions(matrix1, matrix2)` - Get result matrix dimensions

#### `MatrixMultiplicationError`

Custom exception for matrix multiplication errors.

**Properties:**

- `error_type` - Type of error ("dimension_mismatch", etc.)

### Convenience Functions

- `multiply_matrices(matrix1, matrix2)` - Direct multiplication function
- `create_matrix(data)` - Create Matrix object from 2D list

## 🧮 Mathematical Background

Matrix multiplication is defined as follows:

- For matrices A (m×n) and B (n×p), the result C (m×p) is computed as:
- C[i][j] = Σ(k=0 to n-1) A[i][k] × B[k][j]

**Key Rules:**

1. Number of columns in first matrix must equal number of rows in second matrix
2. Result matrix has dimensions: (rows of first) × (columns of second)
3. Matrix multiplication is NOT commutative: A×B ≠ B×A (usually)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎉 Acknowledgments

- ALU (African Leadership University) for the educational opportunity
- Our amazing team members for their creativity and collaboration
- The Python community for excellent tools and documentation

## 📞 Contact

- **Team**: ALU Math Vanguard Group 15
- **Course**: Mathematics for Machine Learning
- **Institution**: African Leadership University

---

_Made with ❤️ and lots of ☕ by Group 15_ 🚀
