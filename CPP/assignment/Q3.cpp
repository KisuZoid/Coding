//1-10 table using loop
#include <iostream>
using namespace std;

int main(){
    for (int i=1; i <= 10; i++) //rows
    {
        for (int j = 1; j <= 10; j++) //coloum
        {
            cout << i * j << " " ;
        } 
        cout << endl;
    }
    return 0;
}