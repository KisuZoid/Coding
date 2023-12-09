#save file I/O
name = input("What is your name? ") 
# open() allows us to what we read from or write to.
# file = open("name.txt", "w") 
    # means open a file named "name.txt" and "w" means formate of name.txt is write , that allows us to change the content of the file.
file = open("name.txt", "a") # "a" mean file will append together with old input. 
file.write(f"{name}\n") #this write() method allows as to write in the "file" variable which is assigned to name.txt
                        #if we just use (name), it will print literally as our input without and extra gap.
                        # (f"{name}\n") file will save from new line each time when we re-run.
file.close() #this close() method will close and save the file(name.txt).
