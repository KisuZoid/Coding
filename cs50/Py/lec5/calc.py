def main():
    x = input("what's x? ")  #input() func. will take the input as str formate by default.
    print("x squared is", square(x))

def square(n):
    return n * n

if __name__ == "__main__":
    main()

