print("Hello, " + input("What is your name? ") + "\n")
x = input("What is your name? ")
print("Hello, "+ x)
y = len(x)
print(y)
print("Number of character in a input string : "+str(y))


"""
    input() function allow user to give the input.
    len() function gives the lenght of the sting, i.e. number of character in a string | it even count whitespaces as well. 
        as len() gives integeral output, so we have to force python to treat it as string so that it will concatenate using + symbol.
        int() represent integer datatype
        str() represent string datatype
        float() represent float datatype
"""