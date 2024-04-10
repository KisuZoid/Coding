#include <iostream>
using namespace std;

double sum(int num1, int num2){
    double c = num1 + num2;
    return c;
}

int main(){
    int value_1, value_2;
    cout << "Number 1: ";
    cin >> value_1;
    cout << "Number 2: ";
    cin >> value_2;
    cout << "The sum of "<< value_1 << " + " << value_2 << " = " << sum(value_1 , value_2);
    return 0;
}