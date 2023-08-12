def main():
    name = input("What's your name? ")
    output = hello(name)
    print(output)

def hello(to = "world"):
    return f"hello, {to}" #f is denoting formate string allows to treat "to" as unique variable.
#if we use print() in place of return then hello() doesn't return anything in 4test_hello.py so we can't test if print() is used.

if __name__ == "__main__":
    main()
