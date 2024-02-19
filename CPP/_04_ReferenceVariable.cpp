#include <iostream>
using namespace std;

int c = 20;

int main(){
    int a,b,c;
    a=3;
    b=4;
    c=5;
    cout << "a+b+c = " << a+b+c << endl;
    cout << "a+b+c (for accessing global c) = " << a+b+::c << endl; 
    
    cout << endl;

// ------Float,Double, and Long Double Literals-------
    float d = 34.4; //34.4 considered as double
    float e = 34.4f; //34.4 condisered as float(use f or F)
    long double f = 34.4; //34.4 considered as double
    long double g = 34.4l; //34.4 considered as long double(use l or L)
   
    cout << "Size of 34.4: " << sizeof(34.4) << endl;
    cout << "Size of 34.4f: " << sizeof(34.4f) << endl;
    cout << "Size of 34.4l: " << sizeof(34.4l) << endl;

    cout << "\n"; // "\n" for new line

//------Reference Variable------
    float x = 455;
    float &y = x; //y is refering x
    cout << x << endl;
    cout << y << endl;

    cout << endl;

//------TypeCasting Variable------
//changing of data type from one to another
int k = 45;
float p = 45.5;

cout << "This is \"k\": " << k << endl; /* "\" is encape keyword, ex: print double quote: use \", direct use of "double quote" will generate error. */
cout << "This is 'k' as an float: " << float(k) << endl;
cout << "This is 'k' as an float: " << (float)k << endl;
cout << "This is \"p\": " << p << endl; 
cout << "This is 'p' as an int: " << int(p) << endl;
cout << "This is 'p' as an int: " << (int)p << endl;

    return 0;
}