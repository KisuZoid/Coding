#3
name = input("What is your name? ").title().strip()
print("Hello, ",end = "")

# split user's name into first name and last name
first, last = name.split(" ")
print(first,"\n")

#or

print(f"Hello, {name}")
print("MY, \"friend\" " + "How are you?",first)


# In python documentation, there is end="\n" in print function that makes a new line after the output.
# Here, using end="" , we modified the print function by erasing "\n" to prevent new line after output.
# \n is used for new line.
# \t is used for tab.     
# similarly, we modified the documentation as pr our need.
#we can use double quote and single quote both as well.
#print("Hello, "friend"") this will give syntax error coz double quote is seems to close after friend.
#to fir that error , print('Hello, "friend"') can be used
#or 
# use print("MY, \"friend\"") "\" back slace is a scaping character
#f in line 10, indicate format that whatever in curl bracket is special string
#print(first) gonna print the first input of name
#first, last is variable indicate first and second input value for name that splitted by a single blank
#split(" ")single blank between quotes incicate the single blank in input of first and last words for name variable, extra blank/input gives error. 
#split() gonna return a sequence of values ideally a first name or a last name