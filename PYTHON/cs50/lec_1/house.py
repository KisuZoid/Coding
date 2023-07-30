#match keyword
name = input("What's your name? ").title().strip()

match name:
    #match variable "name" with all the cases case "Harry" means name associates with Harry there.
    case "Harry" | "Hermione" | "Ron":
        print("Garud Dwar")
    
    #or 

    #case "Harry":
     #   print("Garud Dwar")
    #case "Hermione":
     #   print("Garud Dwar")
    #case "Ron":
     #   print("Garud Dwar")
    case "Draco":
        print("Nagsakti")  
    case _:
        # _ (single underscore character) here it is used to denote that cases which is not specified yet
        print("Who?")  

#or 

"""
name = input("What's your name? ")

if name == "Harry" or name == "Harmione" or name == "Ron":
    print("Garud Dwar")

#or
    
#if name == "Harry":
 #   print("Garud Dwar")
#elif name == "Harmione":
 #   print("Garud Dwar")
#elif name == "Ron":
 #   print("Garud Dwar")
elif name == "Draco":
    print("Nagsakti")
else :
    print("Who?")
"""
