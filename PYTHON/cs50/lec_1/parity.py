def main():
    x = int(input("What's x? "))
    if is_even(x):
        print("Even")
    else:
        print("odd")

def is_even(n):
    if n % 2 == 0:
        return True
    else:
        return False

main()


"""
def main():
    x = int(input("What's x? "))
    x = n(x)

def n(n):
    if n % 2 == 0:
        print("Even")
    
    else:
        print("Odd")

main()
"""

#bool stands for boolean value i.e. true or false

"""
if x % 2 == 0:
    print("Even")
#x % 2 == 0 i.e. x modulo 2 equals to 2 means x divided by 2 and gives reminder 0.
else:
    print("odd")
"""