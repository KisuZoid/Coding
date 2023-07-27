#ask user for their name
name = input("What is your name? ")
name = "Hello, " + name.title().strip() + "!"

#say hello to the user
print(name)
print("How are you? ")

"""
name = name.title().strip()
print("Hello,",name + "!")

print("Hello, " + name + "!")
"""


#name is variable here for input() function.
#input() is a function that takes input.
#print() is the function for output to the screen.
#title() is a function that make first letter of every word capital. 
#strip() is a function that erase whitespaces from both left and right ends.
#upper() function is for making every word capital.
#lower() function is for making every word small.
#lstrip() func. is for removing left end's whitespaces.
#rstrip() func. is for removing right end's whitespaces.
#parentheses after function is for add aditional information to perform by functions. 