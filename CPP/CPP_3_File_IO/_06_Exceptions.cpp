#include <iostream>
using namespace std;

int main(){
    try{
        int age;
        cout << "Your Age: ";
        cin >> age;
        if (age >= 18){
            cout << "Access granted";
        }
        else
        {
            throw (505);
        }
    }
    catch(...){
        cout << "Access denied, make sure you are atleast 18. \n";
    }
    return 0;
}

//throw type is unknown