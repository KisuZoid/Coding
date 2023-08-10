#2
def main():
    x = get_int()
    print(f"x is {x}") 
    
        

def get_int():
    while True: #while True is for infinite loop till condition is True
        try:
            x = int(input("What is x? "))
            #we can use "break" here also and erase else statement. coz for no ValueError, loop will break as value of x is defined. if it give exception like ValueError then except keyword will activate and loop goes on.
        except ValueError:
            print("x is not an integer.\n")
        else:
            return x
#or
#        else:
#            break   #break stands for break the loop.
#    return x   #condition is false, return x to the function

main()
