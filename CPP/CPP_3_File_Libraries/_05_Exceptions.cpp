#include <iostream>
using namespace std;

int main(){
    try{
        int age;
        cout << "Your Age: ";
        cin >> age;
        if (age >= 18){
            cout << "Access granted";
        }
        else
        {
            throw (age);
        }
    }
    catch(int givenAge){
        cout << "Access denied, make sure you are atleast 18. \n";
        cout << "Age is " << givenAge;
    }
    return 0;
}

/*
--> Dealing with errors.
--> When an error occurs, C++ will normally stop and generate and error message --> C++ will throw an exception(throw an error).

--> Exception Handling in C++ consist of 3 keywords: try, throw and catch.
    1. "try" : define a block of code to be tested for errors while it is being executed.
    2. "throw" : throw an exception when a problem is detected, which lets us create custom error.
    3. "catch" : define a block of code to be executed, if an error occurs in the try block.

Syntax:

try{
    //block of code to try

    throw exception:
        //thow an exception when problem arise.
}
catch(){
    //block of code to handle errors
}
*/

//if throw type is unknown, then use 3 dot syntax inside catch. catch(...){}