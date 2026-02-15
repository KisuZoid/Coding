# Solve system of equations using Jacobi method
#
# Jacobi method:
# New values are calculated using only previous iteration values
# Slower than Gauss-Seidel but easier to understand

import numpy as np

A = np.array([
    [27, 5, -3],
    [1, -2, 7],
    [6, 15, 1]
], dtype=float)

B = np.array([45, 70, 29], dtype=float)

x = np.zeros(3)
tolerance = 1e-6
max_iter = 500

for i in range(max_iter):
    x_new = np.zeros(3)

    x_new[0] = (B[0] - (A[0][1]*x[1] + A[0][2]*x[2])) / A[0][0]
    x_new[1] = (B[1] - (A[1][0]*x[0] + A[1][2]*x[2])) / A[1][1]
    x_new[2] = (B[2] - (A[2][0]*x[0] + A[2][1]*x[1])) / A[2][2]

    if np.linalg.norm(x_new - x) < tolerance:
        break
    x = x_new

print("Solution:", x_new)
