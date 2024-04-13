#include <iostream>
using namespace std;

//Base class
class Employee{

    public:
        int id;
        float salary;

        Employee(){}; //default constructor should be necessary to use inherited class, coz inherited class call the base class constructor.
        Employee(int inputID){
            id = inputID;
            salary = 34.0;
        }
};

//creating derived class(Programmer) from Employee class
class Programmer : Employee{
    public:
        Programmer(int inpID){
            id = inpID;
        }
        int languageCode = 9;

        void getData(){
            cout << id << endl;
        }
};

int main(){
    Employee kisu(1), anand(2);

    cout << kisu.salary << endl;
    cout << anand.salary << endl; 

    Programmer skillf(10);
    cout << skillf.languageCode << endl;
    skillf.getData();

    // cout << skillf.id; --> this will throw error as we inherit base class privately by default and id is part of base class.

    return 0;
}

//derived class syntax
/*
class derived-class_name : visiblility_mode base-className 
{
     //members 
}

Note:
    1. default visibility mode is private.
    2. public visibility mode: public members of the base class become public members of the derived class.
    3. private visibility mode: public members of the base class become private members of the derived class.
    4. private member of base class can not be inheritated

*/