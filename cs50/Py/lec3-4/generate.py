#import random  #this import random will import all the random function from module.
from random import choice #this will import only choice function from all random function directory 

#coin = random.choice(["head", "tail"])  #if we import random only then we have to specify here random.choice()

coin = choice(["head", "tail"]) #gives random choice in the the list values.
print(coin)