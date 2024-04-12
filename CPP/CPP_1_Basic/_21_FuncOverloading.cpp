#include <iostream>
using namespace std;

int add(int a, int b){
    cout << "Using func. with 2 agrs." << endl;
    return a+b;
}

int add(int a, int b, int c){
    cout << "Using func. with 3 agrs." << endl;
    return a+b+c;
}

int main(){
    cout << "The sum of 3 and 6 is " << add(3,6) << endl;
    cout << "The sum of 3, 4 and 5 is " << add(3,4,5) << endl;

    return 0;
}

//function overloading is a process to make more than one function with same name but different parameters, numbers or sequences. 