#include <iostream>
using namespace std;

class Base1{
    public:
    void greet(){
        cout << "How are you!! " << endl;
    }
};

class Base2{
    public:
    void greet(){
        cout << "Kaise ho!! " << endl;
    }
};

//same function name for both function create ambiguity
class Derived : public Base1, public Base2{
    public:
        void greet(){
            Base1 :: greet(); // --> means compiler will run greet() func of Base1 class.
        }
};

class X{
    public:
        void say(){
            cout << "Hello World" << endl;
        }
};

class Y : public X{
    public:
    //Y's new say() method will override base class's say() method
        void say(){
            cout << "Hello Dear" << endl;
        }
};

int main(){
    Base1 a;
    Base2 b;
    Derived c;

    a.greet();
    b.greet();
    c.greet();
    
cout << endl;

    X x;
    Y y;
    x.say();
    y.say();
    return 0;
}