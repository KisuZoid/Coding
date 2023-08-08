students = [
    {"name": "Hermione", "house": "Garud Dwar", "patronus": "Otter"},
    {"name": "Harry", "house": "Garud Dwar", "patronus": "Stag"},
    {"name": "Ron", "house": "Garud Dwar", "patronus": "Jack Russell Terrier"},
    {"name": "Draco", "house": "Nagsakti", "patronus": None} #None keyword in python indicate absence of a value
]

for student in students:
    print(student["name"], student["house"], student["patronus"], sep=", ")