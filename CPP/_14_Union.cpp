#include <iostream>
using namespace std;

union money 
{
    /* data */
    int rupee;
    float dollar;
};


int main(){
    union money m1;
    m1.rupee = 5000;
    cout << m1.rupee;
cout << endl;
    union money m2;
    m2.rupee = 4000;
    m2.dollar = 57.62;
    cout << m2.dollar;
    //cout << m2.rupee will generate wrong value because when we set dollar down to the rupee, it will overwrite rupee with dollar.

    return 0;
}

//Union is same as struct, but provide better memory management  --> we gonna use one data type at a time.