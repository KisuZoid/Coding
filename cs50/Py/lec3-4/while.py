#2
while True:
    try:
        x = int(input("What is x? "))
    except ValueError:
        print("x is not an integer.\n")
    else:
        break

print(f"x is {x}")

#while True is for infinite loop till condition is True