#include <iostream>
using namespace std;

class Test{
    int a;
    int b;
    public:
    // --> these all can run 
        //Test(int i, int j) : a(i), b(j) --> a = i and b = j
        //Test(int i, int j) : a(i), b(i+j) --> a = i and b = i+j
        //Test(int i, int j) : a(i), b(2*j) --> a = i and b = 2*j

        Test(int i, int j) : a(i), b(a+j){
            cout << "Constructor executed" << endl;
            cout << "Value of a is " << a << endl;
            cout << "Value of b is " << b << endl;
        }

        // Test(int i, int j) : b(j), a(b+i)  -->Red flag, it will create garbage value, as a is initialized 1st(as int a is upper to int b) means it will execute first before b.
};

int main(){
    Test t(4, 6);

    return 0;
}

/*
Syntax for initialization list in constructor:
constructor(argument-list) : initialization-section
{
    assignment + other code;
}

class Test{
    int a;
    int b;
    public:
        Test(int i, int j) : a(i), b(j){
            //constructor code
        }
};
*/