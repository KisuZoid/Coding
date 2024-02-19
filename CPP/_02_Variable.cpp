#include <iostream>
using namespace std;

int main(){
    //variable declaration
    string name;
    int age;
    
    //Output What is your name? to the screen.
    cout << "What is your name? ";
    // Input from user and assigned to name variable.
    cin >> name;

    cout << "What is your age? "; /* << this is insertion operator*/
    cin >> age; /* >> this is extraction operator*/

    cout << "Your name is " << name 
         << " and you are " 
         << age << " years old.";

    return 0;
}

/*
# Variable is just a container for the particular value.
ex: Primary we have 5 data types:
    1. "int" for intergral data type.
    2. "float" for floating point values of low precision.
    3. "double" for storing larger float value(high precision).
    4. "bool" for boolean values(True(1) or False(0))
    5. "char" for single character. 'A' : written inside single quotes.

//Combination of "char" is "string"
    "string" for string data type. "Kisu" : written inside double quotes.

Syntax:
//Declaration of variable
    dataType variableName;

//Initializing the value
    variableName = value;

--or--

//Declaration and Initializing at same time
    dataType variableName = value;

-> ex:
        int num = 5; // means assign 5 to variable "num" which contains integral values.
        string name = "Kisu"; // means assign Kisu to variable "name" which contain string of characters.

# Variable Scope:
    : A variable region in a program where the existence of that variable is valid.

    -> Local variables:
        : it declared inside the braces of any function and can be accessed only from that particular function.

    -> Global Variable:
        :  it is declared outside any function and can be accessed from everywhere.

    *Name of local and global variable can be same, but value of variable will determined by Local value.

# Data Type: (3 types)
    1. Built-in : int, float, double, bool, char ...
    2. User-defined : Class, Struct, Union, Enum ...
    3. Derived: Array, Function, Pointer ...

#Naming of Variable:
    1. Range 1-255 characters.
    2. Must begin with a letter of the alphabet or an underscore(_).
    3. It contain letters and numbers.
    4. Case sensitive.
    5. No spaces and special charcaters are allowed.
    6. Can't use reserved keyword(variable name inside code documentation).
    
    Note: Name should be clear and describing its functionality.
        ex: //variable for age
            int a; -> wrong approach
            int age; -> correct approach
*/