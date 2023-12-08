#2
def main():
    number = get_number()
    meow(number)

def get_number():
    while True:
        n = int(input("what is n? "))
        if n>0:
            break
    return n
    
def meow(n):
    for _ in range(n):
        print("meow")

main()

'''
#infine loop
while True:
    n = int(input("What's n? "))
    if  n > 0:
        break
    #or
"""
    if n < 0:
        continue #continue(keyword) indicated continue the loop
    else:
        break #break(keyword) is for breaking the most recently begun loop
"""
    

for _ in range(n):
    print("meow")
'''