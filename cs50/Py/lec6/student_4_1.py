#same as student_4 with shorting
students = []

with open("student.csv") as file:
    for line in file:
        name, house = line.rstrip().split(",")
        #creating a dictionary whose key is name and house and value for that is name and house repectively
        """
        student = {}
        student["name"] = name
        student["house"] = house
        """
        student = {"name": name, "house": house}
        students.append(student)
        

for student in students:
    print(f"{student['name']} is in {student['house']}")