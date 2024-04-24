#include <iostream>
using namespace std;

class BaseClass{
    public:
        int var_base = 1;
        virtual void display(){
            cout << "Displaying Base class variable var_base " << var_base << endl;
        }
};

class DerivedClass : public BaseClass{
    public:
        int var_derived = 2;
        void display(){
            cout << "Displaying Derived class variable var_derived " << var_derived << endl;
            cout << "Displaying Derived class variable var_base " << var_base << endl;
        }
};


int main(){
    BaseClass * base_class_pointer;
    BaseClass obj_base;
    DerivedClass obj_derived;

    base_class_pointer = &obj_derived;
    base_class_pointer->display(); //before using virtual, it will display base function's display() --> this is a default behaviour that to display base class.
                                    //After using virtual keyword in base class's display(), it will display derived class function's display.

    return 0;
}