#include <iostream>
using namespace std;

class Number{
    int a;
    public:
        Number(){
            a = 0; //assign a = 0 by default(if no parenthesis is given.) 
        };
        Number(int num){
            a = num;
        }

        //Copy Constructor
        Number(Number &obj){
            cout << "Copy Consructor called!!" << endl;
            a = obj.a; //assign "a" to 'a' of this object "obj" 
        }

        void display(){
            cout << "The number for this object is " << a << endl;
        }
};

int main(){
    Number x, y, z(45), z2;
    x = Number(500);
    x.display();
    y.display(); //use value of default constructor coz nothing is assigned to it.
    z.display();

cout << endl;

    // z1 should exactly resemble z --> we use copy constructor.
    Number z1(z);
    z1.display(); //copy constructor invoked

cout << endl;

    z2 = z; //copy constructor is not called
    z2.display();

cout << endl;

    Number z3 = z; //copy constructor invoked
    z3.display();

    return 0;
}

//when no copy constructor is found, compiler supply its own copy constructor.

//when no constructor is found, compiler supply its own default constructor.