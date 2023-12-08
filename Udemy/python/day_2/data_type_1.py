#string

print("Kisu"[0])
print("123" + "456" + " Kisu")

user_name = "Kisu Zoid"
print(user_name[0] + user_name[5])

#integer

print(123 + 456)

# finding the data type.

num_char = len(input("What is your name? "))

print(type(num_char))

new_num_char = str(num_char)
print("your name has " + new_num_char + " characters")

# [] represents array and count of an array starts with 0(zero)
# print(len(1234)) -> gives error(typeError) object of type "int" as no len()


"""
    Basic Data_Type:
        string  : array of characters
        integer : represents integral numbers
        float   : number with decimal value
        boolean : true(1) or false(0) value 
"""