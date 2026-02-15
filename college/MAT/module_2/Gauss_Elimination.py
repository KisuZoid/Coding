"""
27x+5y-3z=45 
x-2y+7z=70 
6x+15y+z=29
"""

import numpy as np

#coefficiet matrix
A = np.array([
    [27,5,-3],
    [1,-2,7],
    [6,15,1]
], dtype=float)

#constant vector
B = np.array([45,70,29], dtype=float)

#solve using gauss elimination
solution = np.linalg.solve(A, B)

print("x = ", solution[0])
print("y = ", solution[1])
print("z = ", solution[2])

