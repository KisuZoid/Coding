#4
def main():
    name = input("What is your name? ")
    hello()
    hello(name)

#default value of hello() is Hello, world as to is related to world
#main is our main funtion

def hello(to="world"):
    print("Hello,", to)

main()    

#or

"""def hello(to="world"):
    print("Hello,", to)
#default value of to is world, it depend upon us to write default value or not.

name = input("What is your name? ")
hello()
hello(name)"""

#here, name variable resembels with parameter "to" of hello() function

#or 
"""
def hello():
    print("hello,")


name = input("What is your name? ")
hello()
print(name)
"""


#def is for define or creat own function
