#include <iostream>
using namespace std;

class Complex{
    int a,b;

    public:
        // Complex(void); //constructor declaration for default constructor
        Complex(int, int); // constructor declaration for parameterised constructor.

        void printNum()
        {
            cout << "Your number is " << a << " + " << b <<"i" << endl; 
        }
};

Complex :: Complex(int x, int y) // --> This is parametrised constructor.
{
    a = x;
    b = y;

    cout << "Hello World ";
}

/*
Complex :: Complex(void){ // --> This is default constructor as it takes no parameters
    a = 0;
    b = 0;

    
}
*/


int main(){
    //Implicit call
    Complex c(4, 6);
    c.printNum();

    //Explicit call
    Complex d = Complex(5, 7);
    d.printNum();

    return 0;
}