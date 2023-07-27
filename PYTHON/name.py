name = input("What is your name? ")
name = name.title().strip()
print("Hello, ",end = "")
print(name)

# In python documentation, there is end="\n" in print function that makes a new line after the output.
# Here, using end="" , we modified the print function by erasing "\n" to prevent new line after output.
# \n is used for new line.
# \t is used for tab.     