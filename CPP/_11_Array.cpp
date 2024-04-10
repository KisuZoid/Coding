#include <iostream>
using namespace std;

int main(){
    //Method I of defining Array
    int marks[] = {23, 45, 56, 89}; //An Array called marks that contain 4 values. (size is not declared)
    cout << marks[0] << endl;
    cout << marks[1] << endl;
    cout << marks[2] << endl;
    cout << marks[3] << endl;

cout << endl;

    //Method II of definining Array
    int mathMarks[4]; //An Array called mathMarks that contain 4 values. (size is declared)
    mathMarks[0] = 78;
    mathMarks[1] = 58;
    mathMarks[2] = 38;
    mathMarks[3] = 18;

    cout << mathMarks[0] << endl;
    cout << mathMarks[1] << endl;
    cout << mathMarks[2] << endl;
    cout << mathMarks[3] << endl; 

cout<<endl;

    //Changing the value of an Array
    cout << "Previous Value of marks[0] " << marks[0] <<endl;
    marks[0] = 84;
    cout << "New value of marks[0] " << marks[0] <<endl;

cout<<endl;

    //print using loop
    for (int i=0; i<4; i++)
    {
        cout << "The value of marks " << i << " is " << marks[i] << endl;
    }

    return 0;
} 

/*
--> An arrar'[]' is a collection of items of similar type stored in contiguous memory locations 
        Array is 0th indexed.
*/