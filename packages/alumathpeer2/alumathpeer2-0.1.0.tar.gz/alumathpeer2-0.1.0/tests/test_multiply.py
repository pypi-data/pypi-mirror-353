from alumathpeer2 import multiply_matrices

def test_multiply_2x2():
    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    expected = [[19, 22], [43, 50]]
    print(multiply_matrices(A, B))
    assert multiply_matrices(A, B) == expected

test_multiply_2x2()

def test_multiply_2x3_3x2():
    A = [[1, 2, 3], [4, 5, 6]]
    B = [[7, 8], [9, 10], [11, 12]]
    expected = [[58, 64], [139, 154]]
    print(multiply_matrices(A, B))
    assert multiply_matrices(A, B) == expected

test_multiply_2x3_3x2()

def test_multiply_1x3_3x1():
    A = [[1, 2, 3]]
    B = [[4], [5], [6]]
    expected = [[32]]
    print(multiply_matrices(A, B))
    assert multiply_matrices(A, B) == expected

test_multiply_1x3_3x1()

def test_multiply_3x1_1x3():
    A = [[1], [2], [3]]
    B = [[4, 5, 6]]
    expected = [[4, 5, 6], [8, 10, 12], [12, 15, 18]]
    print(multiply_matrices(A, B))
    assert multiply_matrices(A, B) == expected

test_multiply_3x1_1x3()
