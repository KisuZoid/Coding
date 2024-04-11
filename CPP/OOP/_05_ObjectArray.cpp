#include <iostream>
using namespace std;

class Employee{
    int id;
    int salary;

    public:
        void setID(void){
            salary = 122;
            cout << "Enter the ID of employee" << endl;
            cin>> id;
        }
        void getID(void){
            cout << "The ID of this employee is " << id << endl;
        }
};

int main(){
    Employee kisuzoid[4];

    for (int i=0; i<4; i++)
    {
        kisuzoid[i].setID();
        kisuzoid[i].getID();
    }

    return 0;
}