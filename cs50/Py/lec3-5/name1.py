#8
import sys

if len(sys.argv) < 2:
    sys.exit("Too few arguments")

for arg in sys.argv[1:]: #sys.argv have list of values and fir we want to slice the list use sq. bracket and position of values. [1:] means we want to keep values of list from 1 to end.  
    print("hello, my name is", arg)
    #if we use [1:-1] a negative no. means counting to the other direction. let a list x = ["kislay", "anand", "jha"] using [1:-1] syntax, means gonna print from value 1 to the n-1 value of list here n is the total positonal count of values. as list is 0 indexed means in list x has total 4 values (0,1,2,3) here n = 3, so gonna print 1 & 2 no. values.
    #i.e. only print kislay anand (negative means slice from last)