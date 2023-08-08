def main():
    print_square(3)

def print_square(size):
    for i in range(size):
        print("#" * size)
    #or
    """
    #for each row in square
    for i in range(size):
        #for each brick in row
        for j in range(size):
            #print brick
            print("#", end="")
        print() 
    """
#we dont want a new line after every "#", we want new line after a row. there print() helps

main()