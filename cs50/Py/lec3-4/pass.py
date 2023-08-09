#3
def main():
    x = get_int("What's x? ")
    print(f"x is {x}") 
    
def get_int(prompt):
    while True: 
        try:
            x = int(input(prompt))
            return (x)
        except ValueError:
            pass #pass means we don't want to show output just keep prompting "what is x?"
            
main()
