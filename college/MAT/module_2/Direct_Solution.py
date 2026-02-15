# Direct solution using NumPy
# This is used to verify iterative method answers

import numpy as np

A = np.array([
    [27, 5, -3],
    [1, -2, 7],
    [6, 15, 1]
], dtype=float)

B = np.array([45, 70, 29], dtype=float)

solution = np.linalg.solve(A, B)

print("x =", solution[0])
print("y =", solution[1])
print("z =", solution[2])
