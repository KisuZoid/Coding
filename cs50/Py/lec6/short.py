#short the output
#read all the list at once then print after short. one-by-one reading th line will low the process while shorting.

#first create a list in the start to gather my data,
    #then read the all file and append it to our list
        #then short the list and print

names = []

with open("name.txt") as file:
    for line in file:
        names.append(line.rstrip())

for name in sorted(names):
    print(f"hello, {name}")