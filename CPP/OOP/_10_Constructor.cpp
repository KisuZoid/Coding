#include <iostream>
using namespace std;

class Complex{
    int a,b;

    public:
        void printNum(){
            cout << "your number is " << a << " + " << b << "i" << endl;
        }
        
        Complex(void); //constructor declaration
};

//Creating a constructor
Complex :: Complex(void){ // --> This is a default constructor, as it takes no parameter.
    a = 10;
    b = 0;

    cout <<"Kisu ";
}

int main(){
    Complex C;

    C.printNum();

    return 0;
}


//Constructor is a special member with same name as of the class, it is automatically invoked.
    //it is used to initialize the object of its class

/*
Constructor:
    1. it should be declared in public section of the class.
    2. they invokes automatically whenever the object is created.
    3. they can't return values and don't have return type.
    4. it can have default arguments
    5. we can't refer to their address.
*/