# x^3 - 4x + 9 = 0
#
# Bisection method:
# If f(a) < 0 and f(b) > 0, then root lies between a and b
# We repeatedly take middle value until the interval becomes very small

def f(x):
    return x**3 - 4*x + 9

"""
f(-3) < 0
f(-2) > 0
So root lies between -3 and -2
"""

a = -3
b = -2
tolerance = 1e-6
max_iter = 100

for i in range(max_iter):
    c = (a + b) / 2   # middle value
    if abs(b - a) < tolerance:
        break
    if f(a) * f(c) < 0:
        b = c
    else:
        a = c

print("Root =", c)
