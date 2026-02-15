# Solve system of equations using Gauss-Seidel method
#
# 27x + 5y - 3z = 45
#  x - 2y + 7z = 70
#  6x +15y +  z = 29
#
# Gauss-Seidel uses updated values immediately
# This usually converges faster than Jacobi

import numpy as np

A = np.array([
    [27, 5, -3],
    [1, -2, 7],
    [6, 15, 1]
], dtype=float)

B = np.array([45, 70, 29], dtype=float)

x = np.zeros(3)   # initial guess
tolerance = 1e-6
max_iter = 500

for i in range(max_iter):
    x_old = x.copy()

    x[0] = (B[0] - (A[0][1]*x[1] + A[0][2]*x[2])) / A[0][0]
    x[1] = (B[1] - (A[1][0]*x[0] + A[1][2]*x[2])) / A[1][1]
    x[2] = (B[2] - (A[2][0]*x[0] + A[2][1]*x[1])) / A[2][2]

    if np.linalg.norm(x - x_old) < tolerance:
        break

print("Solution:", x)
