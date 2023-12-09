#more appropriate way in place of name_1_1
name = input("what's your name? ")

with open("name.txt", "a") as file: #assign this open() function to file variable
    file.write(f"{name}\n")