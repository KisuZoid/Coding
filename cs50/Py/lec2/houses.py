#dict stands for dictionary that allows to associate one value to the another.
    # for dict dipicition, use { }.

students = {
    "Hermione": "Garud Dwar",
    "Harry": "Garud Dwar",
    "Ron": "Garud Dwar",
    "Draco": "Nagsakti",
}

for student in students:
    print(student, students[student], sep = ", ")
    
'''  
students = {
    "Hermione": "Garud Dwar",
    "Harry": "Garud Dwar",
    "Ron": "Garud Dwar",
    "Draco": "Nagsakti",
}

i = input("Enter the name? ")
print(students[i])
print(students["Hermione"]) 
print(students["Harry"])
print(students["Ron"])
print(students["Draco"])
'''