#5
def main():
    x = int(input("What's x? "))
    print("x squared is", square(x))

def square(n):
    return pow(n, 2)

#return keyword returns a value to  the function

if __name__ == "__main__": #explained in lec3-4 saying.py
    main()


#return n*n | return n ** 2 | return pow(n, 2) here n is no. and 2 indicate power
#all are same