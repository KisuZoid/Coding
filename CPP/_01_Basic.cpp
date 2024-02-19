//Header file
#include <iostream>

//Executable Code block should be inside main() function. 
int main(){
    //print Hello World
    std::cout << "Hello World";
    return 0;
}

/*
Multi 
line 
comment
*/

//Single line comment

/*
# Header files is used for inhance the program functionality.
    #include <iostream> : include the iostream(input output stream) file to the program.
                            that helps in input(cin), output(cout) and other tasks as well.
    
    Function:
        <returnType> <functionName>(parentheses){
            //code block or functionality
        }

        int main(){...} : main() function return integer value to the Operating System(O.S).
                            return 0; means returns 0 to O.S means program is success full, else failed.
                            functionality of main() function will be inside curly braces {}.
    
    : "cout" is the standared output stream, which lies inside standared namespace ("std").
         std::cout means call cout from std.
         ";" is used for terminate the statement.
        
    : If we not want to use "std" before every "std-file" then just use:
        "using namespace std;" after header file.
        or 
        "using std::cout;" after header file, call cout from std which is applicable for all cout function. 
    
    : string should be written inside double quote. "String"

    : There are 2 types of header file:-
        1. system header file: comes with compiler
        2. user defined header file: written by the programmer inside same directory.
            ex: "#include example.h" where example.h is in the current directory as file.
    
    :search cpp reference in search engine.
*/