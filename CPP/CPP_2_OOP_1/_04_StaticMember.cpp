#include <iostream>
using namespace std;

class Employee
{
    int id;
    static int count; // static variable will take memory at once and further update only.
                      // static variable is the property of class not a perticular object.
public:    
    void setData(void)
    {
        cout << "Enter the ID ";
        cin >> id;
        count++;
    }
    void getData(void)
    {
        cout << "The ID of this Employee is " << id << " and this is employee number " << count << endl;
    }

    //static function: the function that access all other static variable or static function
    static void getCount(void){
        cout << "The value of count is "<< count << endl;
        //cout << id; --> gives error, as id is not static
    }
};

// static variable should be defined outside the class
int Employee ::count; // default value is 0 for 1st object and it will update further
// int Employee :: count = 1000; --> //default value become 1000

int main()
{
    Employee kisu, kislay, anand;
    // kisu.id = 1; or kisu.count = 1; --> can't be done as it is private member

    kisu.setData();
    kisu.getData();
    Employee::getCount();

    kislay.setData();
    kislay.getData();
    Employee::getCount();

    anand.setData();
    anand.getData();
    Employee::getCount();

    return 0;
}