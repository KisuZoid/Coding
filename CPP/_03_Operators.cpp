#include <iostream>
using namespace std;

int main(){
    //Arithmetic Operators
    int a=4, b=5;

    cout << "The value of a+b is " << a+b << endl; //endl is for terminating the line.
    cout << "Old value of a = " << a << endl; //4
    cout << "a++ = " << a++ << endl; //now value of a become 4+1= 5
    cout << "New value a = " << a << endl; //5
    cout << "++a = " << ++a <<endl; //now value of a become 1+5 and print.

    //comparision operator
    cout << "a Equals to b: " << (a==b) << endl;
    cout << "a Not Equals to b: " << (a!=b) << endl;

    //logical operator
    a=4, b=5;
    cout << "AND operator: " << ((a<b) && (a!=b))<< endl;
    cout << "OR operator: " << ((a>b) || (a!=b)) << endl;
    return 0;
}

/*
    :Arthmetic Operator
        +,-,*,/,%,++,--
        a+b (add a & b)
        a-b (subtract a & b)
        a*b (multiply a & b)
        a%b (integral reminder when a divided by b)
        a++ (execute "a" then increase by 1 and assign it to "a")
        ++a (increase the value of "a" by 1 and assign it to "a" then execute "a")
        a-- (execute "a" then decrease by 1 and assign it to "a")
        --a (decrease the value of "a" by 1 and assign it to "a" then execute "a")
    
    :Assignment Operator --> used to assign values to the variables
        int a = 3; 3 is assigned to "a" which is integer in nature.
        char d = 'd';

    :Comparision operator --> give result in true(1) or false(0).
        a<b a is less than b
        a<=b a is less than equals to b
        a>b a is greater than b
        a>=b a greater than equals to b  
        a==b a equals to b
        a!=b a not equals to b

    :Logical operator -> give result in true(1) or false(0).
        && AND operator a&&b gives true if both a and b are true.
        || OR operator a||b gives true if any one of a and b is true. 
*/