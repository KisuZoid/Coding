#include <iostream>
using namespace std;

int main(){
    //name of array is the address of first block in case of array.
    // &name --> worng!

    int marks[] = {00,11,22,33};
    int *p = marks;
    cout << "The value of marks[0] is " << *p << endl;
    cout << "The value of marks[1] is " << *(p+1) << endl;
    cout << "The value of marks[2] is " << *(p+2) << endl;
    cout << "The value of marks[3] is " << *(p+3) << endl;

cout << endl;
//another way
    int marksMath[] = {000, 111, 222, 333};
    int *m = marksMath;
    cout << *(m++) << endl;
    cout<< *m << endl;
    cout<< *(++m) << endl;


    return 0;
}
