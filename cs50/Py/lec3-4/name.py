#7
import sys

#check for errors
if len(sys.argv) < 2:
    sys.exit("Too few arguments") #sys.exit will exit my program after printing the string that i have given as input if condition will true.
elif len(sys.argv) > 2:
    sys.exit("Too many arguments")
#print name tags
print("hello, my name is", sys.argv[1])


'''
if len(sys.argv) < 2: #means if length of list sys.argv is less than 2.
    print("Too few arguments")
elif len(sys.argv) > 2:
    print("Too many arguments")
else:
    print("hello, my name is", sys.argv[1])
'''


#argv stands for argument vector, it discribes the list of values that the used input in command till hit enter.
# although list is 0 indexed but if we use 0 in place of 1 will give the name of program. 