x = float(input("x: "))
y = float(input("y: "))

z = x/y
print(f"{z:,.2f}")
#.2f here f is for float value and .2 shows the value till round off after decimal

#4,5 line code is same as below
"""
z = round(x / y, 2)
print(f"{z:,}")
"""
#round function make round off your answer default in integer.
#in documentation round(number[, ndigits]) number and ,ndigits gives till how many value your wanna round off | [] means whatever is written inside parentheses is optional

# :, give U.S no. system representation. i.e. comma after 3 no.
#f"{z:,}" is the format to avoid error
#for integer values, replace float() with int()
#ex: x = int(input("x: "))


"""
x = input("x: ")
y = input("y: ")

z = int(x) + int(y)

#int(x) means x is an integer

print("Result:",z)
"""





#str is class for strings
#in case of string + is for combining to variables
#int is for integers
#in numbers python supports operation like  +,-,%,*
# + is for add | - is for subtract | * is for multiplication
# % is modulo which is for taking reminder
