#include <iostream>
using namespace std;

class Base1{
    protected:
        int base1int;
    public:
        void set_base1int(int a){
            base1int = a;
        }
};

class Base2{
    protected:
        int base2int;
    public:
        void set_base2int(int b){
            base2int = b;
        }
};

class Derived : public Base1, public Base2{
    public:
        void show(){
            cout << "The value of Base1 is " << base1int << endl;
            cout << "The value of Base2 is " << base2int << endl;
            cout << "The sum of values are " << base1int + base2int << endl;

        }
};

int main(){
    Derived num;
    num.set_base1int(5);
    num.set_base2int(2);
    num.show();
    return 0;
}

//syntax:
// class Derived : visibility-mode base1, visibility-mode base2{ //class body }; 

/*
The inherited derived class will look something like this:
Data members:
    base1int --> proctected
    base2int --> proctected
Member functions:
    set_base1int() --> public
    set_base2int() --> public
    show()         --> public

*/