#include <iostream>
using namespace std;

class Base1{
    int data1;
    public:
        Base1(int i){
            data1 = i;
            cout << "Base1 class constructor called " << endl;
        }
        void printDataBase1(void){
            cout << "The value of data1 is " << data1 << endl;
        }
};

class Base2{
    int data2;
    public:
        Base2(int i){
            data2 = i;
            cout << "Base2 class constructor called " << endl;
        }
        void printDataBase2(void){
            cout << "The value of data1 is " << data2 << endl;
        }
};

class Derived : public Base1, public Base2{ //this order matter
    int derived1, derived2;
    public: 
        Derived(int a, int b, int c, int d) : Base1(a), Base2(b){ //here Base1(a), Base2(b) order doesn't matter
            derived1 = c;
            derived2 = d;
            cout << "Derived class constructor data called " << endl;
        }
        void printDataDerived(void){
            cout << "The value of derived1 is " << derived1 << endl;
            cout << "The value of derived2 is " << derived2 << endl;
        }
};

int main(){
    Derived kisu(1, 2, 3, 4);
    kisu.printDataBase1();
    cout << endl;
    kisu.printDataBase2();
    cout << endl;
    kisu.printDataDerived();
    return 0;
}

/*
-->We can use constructor in derived class in C++
-->if base class constructor does not have any arguments, there is no need of any constructor in derived class.
--> But is there are one or more arguments in base class constructor, derived class need to pass arguments to the base class constructor.
--> if both base and derived class have constructors, base class constructor is executed first.
--> The constructor of derived class recieves all the arguments at once and then will pass the calls to respective base classes.
    ==>  derived(args1, args2, arga3, ...) : base1(args1, arg2), base2(arg3, arg4){...}
--> body willmcalled after all the constructors are finished executing.
--> the constructor of virtual base classes are invoked before an nonvirtual base class.

--> if there are multiple assignment then they will call in order they are declared from top to bottom.

case1:
    class A: public B{
        //order of execution of constructor --> First B() then A()
    };

case2:
    class A: public B, public C{
        //order of execution of constructor --> B() then C() and A()
    };

case3:
    class A: public B, virtual public C{
        //order of execution of constructor --> C() then B() and A()
    };

case4:
    class A: virtual public B, virtual public C{
        //order of execution of constructor --> B() then C() and A()
    };
*/