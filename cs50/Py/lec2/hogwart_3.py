#4
#List(count starts from 0)

#len is funtion in python that tells the length of a list in integeral value in pyhton. 
students = ["Hermione", "Harry", "Ron"]

for i in range(len(students)):
    print(i + 1, students[i]) #i give the numeric position to values of students list, as list starts from 0 , so we add 1 for convinience, so that counting starts from 1.


'''
students = ["Hermione", "Harry", "Ron"]

for s in students:
    print(s) # s is a variable denotes values in students variable. and in python it automatically initiate(hermione 1st and continue for next and next values as well.) 
'''

"""
students = ["Hermione", "Harry", "Ron"] #students is a variable for list of 3 student.
#if we want to show particular student let say Hermione so use variable name and position of hermione in sq. bracket. i.e. 0 in this case. 

print(students[0])
print(students)
"""


#List and Array both are mutable and store ordered items.
#List can store element of different types, but arrays can store element of same type.
#List provides more flexibility as it does not require explicit looping, but arrays require explicit looping to print elements. 