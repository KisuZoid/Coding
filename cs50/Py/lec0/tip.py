#tip calculator
#dollar_to_float, which accept a str as input as formate $##.##, where # is a decimal digit, remove $ and return the amount as a float i.e. $50.00 means 50.0
#percent_to_float, which accept a str as input as formate ##%, where # is a decimal digit, remove % and return the percentage as a float i.e. 15% means 0.15
    
def main():
    dollars = dollar_to_float(input("How much was the meal? "))
    percentage = percent_to_float(input("What percentage would you like to tip? "))
    tip = dollars * percentage
    print(f"Leave ${tip:,.2f}")

def dollar_to_float(d): 
   d = d.replace("$", "")
   return float(d)
   

def percent_to_float(p):
   p = p.replace("%", "")
   return float(p)/100
  
   
main()
    
#or
    
"""
def main():
    dollars = dollar_to_float()
    percentage = percent_to_float()
    tip = dollars * percentage
    print(f"Leave ${tip:,.2f}")

def dollar_to_float():
   x = input("How much was the meal? ")
   x = x.replace("$", "")
   return float(x)
   

def percent_to_float():
   y = input("What percentage would you like to tip? ")
   y = y.replace("%", "")
   return float(y)/100
  
   
main()
"""
#replace() function replaces values i.e. replace("1","2") means replace 1 with 2.
#replace() method is valid for strings only therefore variable defined as float after the replace method
