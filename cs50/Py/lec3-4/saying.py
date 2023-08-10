#12
#creating our own library
def main():
    hello("world")
    goodbye("world")

def hello(name):
    print(f"hello, {name}")

def goodbye(name):
    print(f"goodbye, {name}")

if __name__ == "__main__":
    main()

#if we just blindly put main only then when this file is import somewhere, first it will run and give output then that importer file will give there output.
#so for preventing that output problem, we use "if __name__ == "__main__":" 2 underscores are used here.
# __name__ is the special variable whose value is automatically set by python to be "main" when we run this file directly using its name i.e. "python saying.py". but if we import this file means we are not runing this file by its name so "main()" at the end will be ignored. that solve the problem.