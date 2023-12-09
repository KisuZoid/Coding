#csv(comma seperated value) is a kind of convention that "," seperates the values this is like row 1st and row 2nd.
with open("student.csv") as file:
    for line in file:
        name, house = line.rstrip().split(",") #split(",") means split words before and after th comma. 
        print(f"{name} is in {house}")
