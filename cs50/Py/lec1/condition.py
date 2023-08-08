#1
x = int(input("What's x? "))
y = int(input("What's y? "))

if x<y or x>y:
    print("x is not equal to y.")

# or

#if x != y:
#    print("x is not equal to y.")

if x < y:
    print("x is less than y")

elif x > y:
    print("x is greater than y")

else:
    print("x is equal to y")

# elif is for else if. it makes program faster a bit coz once we got answer, running of code will stop there(no need to run complete code).

#syntax :
# > means greater that
# >= means greater that equals to
# <= less than equals to
# == means equals to
# != not equals to