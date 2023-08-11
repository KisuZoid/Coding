#7
def main():
    h = int(input("Height: "))
    print_column(h)
    w = int(input("Width: "))
    print_row(w)
   

def print_column(height):
    print("#\n" * height, end = "")
#or
'''
def print_column(height):
    for _ in range(height):
        print("#")
'''
def print_row(width):
    print("?" * width)
    
main()
    

"""
for _ in range(3):
    print("#")
#or
print("#")
print("#")
print("#")
"""