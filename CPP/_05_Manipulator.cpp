#include <iostream>
#include <iomanip> //for using manipulator
using namespace std;

int main(){
    //Constants in c++ :- value can't be change further inside the code.
    const int a = 3; //a=3 is fixed for the program.

    //Manipulator
    int b = 43, c = 1234;
    cout << "The value of a without setw manipulator: " << a << endl;
    cout << "The value of b without setw manipulator: " << b << endl;
    cout << "The value of c without setw manipulator: " << c << endl;

    cout << "The value of a setw manipulator: " << setw(4) << a << endl;
    cout << "The value of b setw manipulator: " << setw(4) << b << endl;
    cout << "The value of c setw manipulator: " << setw(4) << c << endl;
    return 0;
}

//Manipulator:
/*
endl
It is used to enter a new line with a flush.

setw(a)
It is used to specify the width of the output.

setprecision(a)
It is used to set the precision of floating-point values.

setbase(a)
It is used to set the base value of a numerical number.
*/