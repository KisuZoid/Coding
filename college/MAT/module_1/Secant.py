# x^3 - 4x + 9 = 0
#
# Secant method:
# Similar to Newton-Raphson but derivative is NOT required
#
# Formula:
# x(n+1) = x(n) - f(x(n))*(x(n)-x(n-1)) / (f(x(n))-f(x(n-1)))

def f(x):
    return x**3 - 4*x + 9

"""
We take two initial values where function changes sign
x0 = -3
x1 = -2
"""

x0 = -3
x1 = -2
tolerance = 1e-6
max_iter = 100

for i in range(max_iter):
    x2 = x1 - f(x1)*(x1 - x0)/(f(x1) - f(x0))
    if abs(x2 - x1) < tolerance:
        break
    x0 = x1
    x1 = x2

print("Root =", x2)
