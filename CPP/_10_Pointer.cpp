#include <iostream>
using namespace std;

int main(){
    //What is pointer? --> data type which holds the address of otherdata types

    int a=3;
    int *b=&a; //means b is a pointer integral variable that points to address of 'a'

    //& --> Address of operator
    cout << "The address of 'a' " << &a << endl;
    cout << "The address of 'a' " << b <<endl;

    //* --> (value at) Dereference operator
    cout << "The value at address 'b' is " << *b <<endl;

    //pointer to pointer variable :- a pointer that store address of other pointer.
    int **c = &b;
    cout << "The address of 'b' is " << &b<< endl;
    cout << "The address of 'b' is " << c<< endl;
    cout << "The value at address 'c' is "<< *c <<endl;
    cout << "the value at address value_at(value_at(c)) is " << **c <<endl;

    return 0;
}