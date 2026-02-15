# x^3 - 4x + 9 = 0
#
# Fixed point method:
# Rewrite equation in form x = g(x)
#
# One possible form:
# x = (4x - 9)^(1/3)

def g(x):
    value = 4*x - 9
    # cube root handling for negative values
    return (abs(value))**(1/3) * (1 if value >= 0 else -1)

"""
Initial value taken from earlier methods
x0 = -2.5
"""

x0 = -2.5
tolerance = 1e-6
max_iter = 100

x = x0
for i in range(max_iter):
    x_new = g(x)
    if abs(x_new - x) < tolerance:
        break
    x = x_new

print("Root =", x_new)
