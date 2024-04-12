#include <iostream>
using namespace std;

void swap(int x, int y) //temp x y
{                       // 4   4 5
    int temp = x;       // 4   5 5
    x = y;              //4    5 4
    y = temp;
}

//call by reference by pointers.
void swapPointer(int *x, int *y)
{
    int temp = *x;
    *x = *y;
    *y = temp;
}

//call by reference using C++ reference variable.
void swapReferenceVar(int &x,int &y)
{
    int temp = x;
    x = y;
    y = temp;
}

int &returnReference(int &x, int &y) //means we are returning a reference variable
{
    int temp = x;
    x = y;
    y = temp;
    return x;
}

int main(){
    int a=4, b=5;
    cout << "The Value of a is " << a << endl << "The value of b is " << b << endl;

cout<<endl;

    swap(a,b); 
    cout << "New Value of a using swap() is " << a << endl;
    cout << "New Value of b using swap() is " << b << endl;
    //this will not swap a and b.

cout<<endl;
    //call by reference by pointers.
    //this will swap a and b using pointer reference.
    swapPointer(&a,&b); 
    cout << "New Value of a using swapPointer() is " << a << endl;
    cout << "New Value of b using swapPointer() is " << b << endl;

cout << endl; 
    a=4, b=5;
    //call by reference using C++ reference variable.
    //this will swap a and b using C++ reference variable.
    swapReferenceVar(a,b);
    cout << "New Value of a using swapReferenceVar() is " << a << endl;
    cout << "New Value of b using swapReferenceVar() is " << b << endl;

cout << endl;
    a=4, b=5;
    //Return by reference
    //value of a become 550 as this function returns reference of a which is equal to 550.
    returnReference(a,b) = 550;
    cout << "New Value of a using returnReference() is " << a << endl;
    cout << "New Value of b using returnReference() is " << b << endl;

    return 0;
}