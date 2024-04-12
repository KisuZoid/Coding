#include <iostream>
using namespace std;

//Function prototype
//DataType functionName(arguments);
void greet(string name);
double sum(int num1, int num2); // this is a prototype for sum function that gives assurity that it is present in program.

int main(){
    int value_1, value_2; //value_1 and value_2 are actual parameters.
    string Name;
    cout << "What is your name? ";
    cin >> Name;
    greet(Name);
cout << endl;
    cout << "Enter Number 1: ";
    cin >> value_1;
    cout << "Enter Number 2: ";
    cin >> value_2;
    cout << "The sum of "<< value_1 << " + " << value_2 << " = " << sum(value_1 , value_2);
    return 0;
}

//function that returns something -> here it is returning double.
double sum(int num1, int num2){
    //num1 and num2 will be taking values from actual parameters value_1 and value_2.
    double c = num1 + num2;
    return c;
}

//function that return nothing -> i.e. return void
void greet(string name){
    cout << "Hello " << name << endl;
}