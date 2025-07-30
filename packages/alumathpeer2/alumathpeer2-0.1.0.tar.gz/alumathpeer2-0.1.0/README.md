# AluMathPeer2

A simple and efficient matrix multiplication library.

## Installation

```bash
pip install alumathpeer2
```

## Usage

```python
from alumathpeer2 import multiply_matrices

# Example 1: 2x2 matrices
A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
result = multiply_matrices(A, B)
# Result: [[19, 22], [43, 50]]

# Example 2: 2x3 and 3x2 matrices
A = [[1, 2, 3], [4, 5, 6]]
B = [[7, 8], [9, 10], [11, 12]]
result = multiply_matrices(A, B)
# Result: [[58, 64], [139, 154]]
```

## Features

- Supports matrices of different dimensions
- Input validation
- Simple and intuitive API

## License

MIT License
