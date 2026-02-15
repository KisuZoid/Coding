# x^3−4x+9=0

#function
def f(x):
    return x**3 - 4*x + 9

#differentiation of f(x)
def df(x):
    return 3*x**2 - 4

"""
f(-3) < 0 and f(-2) > 0 -> root lies between -3 and -2

average= ((-3)+(-2))/2 => -2.5 <- initial guessed solution

Newton - Raphson formula:
x"n+1" = x"n" - f(x"n")/f'(x"n") -> f'() => df()
"""

x0 = -2.5 #initial guess
tolerance = 1e-6 #Stop when the error is smaller than this value i.e error<0.000001
max_iter = 20 #max repetition of the numerical formula

x = x0
for i in range(max_iter):
    x_new = x - f(x)/df(x)
    if abs(x_new - x) < tolerance:
        break
    x = x_new

print("Root = ", x)
