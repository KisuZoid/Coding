#include <iostream>
using namespace std;

int main(){
    //Basic Example
    int a = 4; //&a refering to a i.e. address of a.
               //*ptr address storage container
    cout << "The value of a: " << a << endl;
    cout << "The address of a in memory: " << &a << endl;

    int *ptr = &a;
    cout << "The value of pointer ptr that points to a: " << ptr << endl;
    cout << "The value at address ptr is : " << *ptr << endl; //*ptr same as *(ptr) --> dereference    

cout << endl;

    //new Keyword/operator --> used to allocate memory at runtime. i.e. dinamically allocation of memory
    int *p = new int(40);
    cout << "The value of pointer p that points to int 40: " << p << endl;
    cout << "The value at address p is " << *p << endl;

cout << endl;

    int *arr = new int[3];
    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    cout << "The value of arr[0] is " << arr[0] << endl;
    cout << "The value of arr[1] is " << arr[1] << endl;
    cout << "The value of arr[2] is " << arr[2] << endl;
    cout << "The value at address arr is " << arr << endl;

cout << endl;

    //delete keyword/operator --> it will freeup the block of dynamically allocated memory.
    delete arr;
    //delete[] arr;
    cout << "The value of arr[0] is " << arr[0] << endl;
    cout << "The value of arr[1] is " << arr[1] << endl;
    cout << "The value of arr[2] is " << arr[2] << endl;
    cout << "The value at address arr is " << arr << endl;

    //for deletion of whole contiguious memory use "delete[] <name>"


    return 0;
}