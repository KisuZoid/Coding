#1
try:
    x = int(input("What's x? "))
except ValueError:
    print("x is not an integer")
else:
    print(f"x is {x}")
    #ValueError is due to int() func. if input value is not integer. 
    # "=" means copy the value of right side and pasted it on left. but due to ValueError, there is no value remain for copy and paste.
    #and in case of ValueError, we write same code without else statement, give x not difined coz = sign is failed to copy and paste the value.
  
#or

"""
try: 
    x = int(input("What is x? "))
    print(f"x is {x}") #f stands for formate string of f string shows that wht ever is in curly bracket, treat it differently i.e mentioned in code.

except ValueError: #we mention here that exceptional thing is ValueError, if that will happen then print next line
    print("x is not an integer")
#ValueError these are case sensitive words, V and E must me capital here.
"""


#python also has a keyword called try and except, literal meaning is to try, and we can check wether or not something exceptional has happen.
#if something exceptional happen then print("this")
#try and except syntax also support else.
