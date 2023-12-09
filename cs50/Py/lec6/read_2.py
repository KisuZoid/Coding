#read the file
with open("name.txt", "r") as file: # open the file name.txt in reading formate and aign it to file variable.
    lines = file.readlines() #readlines() this method comes with open() method to read the file. 

for line in lines: #lines is a list and line is a variable which automatically set to 1st element to last. (tipical for loop in python)
    print("hello,", line.rstrip()) #rstrip() will strip off the end of the line same as end="".