#include <iostream>
using namespace std;

int factorial(int n){
    if ((n>=0) && (n<=1)){
        return 1;
    }
    return n*factorial(n-1);
}

int main(){
    //Factorial of a number using recurssion:
    int num;
    cout << "Find factorial of a number: ";
    cin >> num;
    
    cout << "Factorial of " << num << " is " << factorial(num);
    return 0;
}

//recurssive function: the function which is calling itself.