#3
#for loop
for _ in range(3):
    print("meow")
#range(n) function gives a range of values and here the range is n and starts from 0 till n-1. n indicate n no. of values. 
#range input is a integer value.
# variable _ is a kind of variable that used when wwe not concern about name of variable.

"""
for i in [0, 1, 2]:
    print("meow") 
""" 
#means for loop 1: i = 0, loop 2: i = 1, loop 3: i = 2 and for each loop, print meow
#for loop allows to iterate over list of items
#[0, 1, 2] square bracket indicates a list. 0,1,2 is the items of the list

print("or") #or 

print("meow\n" * 3, end = "") 
print("meow" * 3 + "meow"+"meow"+"meow")#as this print func. create extra blank line in the end so we use end value to erase that new line.
#print("meow"*3) means add meow 3 times with zero seperation i.e meowmeowmeow. so use \n for to make each meow on new line
