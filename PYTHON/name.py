name = input("What is your name? ")
name = name.title().strip()
print("Hello, ",end = "")
print(name)
print("MY, \"friend\" "+"How are you?",name)

# In python documentation, there is end="\n" in print function that makes a new line after the output.
# Here, using end="" , we modified the print function by erasing "\n" to prevent new line after output.
# \n is used for new line.
# \t is used for tab.     
# similarly, we modified the documentation as pr our need.
#we can use double quote and single quote both as well.
#print("Hello, "friend"") this will give syntax error coz double quote is seems to close after friend.
#to fir that error , print('Hello, "friend"') can be used
#or use print("MY, \"friend\"")
