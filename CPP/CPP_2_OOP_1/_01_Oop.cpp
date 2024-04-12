#include <iostream>
using namespace std;

class Employee
{
    private:
        int a,b,c;
    
    public:
        int d,e;
        //setter declaration
        void setData(int a1, int b1, int c1); //decleration that this function may provide outside separetely.
        //getter
        void getData(){
            cout << "The value of a is " << a << endl;
            cout << "The value of b is " << b << endl;
            cout << "The value of c is " << c << endl;
            cout << "The value of d is " << d << endl;
            cout << "The value of e is " << e << endl;
        }
};

//setter 
void Employee :: setData(int a1, int b1, int c1){ //we are accessing that setData function which is part of Employee using scope resolution operator (::). 
    a = a1;
    b = b1;
    c = c1;
}

int main(){
    Employee kisu;
    kisu.setData(1,2,3);
    kisu.d = 4;
    kisu.e = 5;
    //kisu.a --> we can't access 'a' 

    kisu.getData();
    return 0;
}

/*
    private: by default data type, and it can be access only within  its own class.
    protected: it can be access within or by any other classes.
    public: it can be access through out anywhere.

    to access private data, we use setter and getter, we can't get or set private data directely.

    *Oop -> Object Oriented Programming (Class and object)
    *class --> extention of structures with more security.
    *structure had limitations
        --> members are public
        --> No methods
    *class --> structure + more, can have methods and properties
    *class --> can make few members as private & few as public and protected as well.
    *we can declare object along with class declaration.
        class Employee{
            //class data
        } kisu, kislay, anand;

        --> kisu, kislay and anand are the object of this class Employee.
*/