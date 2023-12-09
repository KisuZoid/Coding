names = []

for _ in range(3):
    name = input("What's your name? ")
    names.append(name) # append() method will use to add elements in the last of our list items. 
for name in sorted(names): # sorted()  will short the values in alphabetical order.
    print(f"Hello, {name}")
    