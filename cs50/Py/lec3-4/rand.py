#5
import random

cards = ["jack", "queen", "king"]
random.shuffle(cards) #shuffle the values in the list and return none.

for card in cards:
    print(card) #for loop with print(card) is showing all three shuffled cards in each loop.

'''
number = random.randint(1, 10) #gives random output from 1 to 10.
print(number)
'''