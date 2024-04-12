#include <iostream>
using namespace std;

class Simple
{
    int data1, data2;

    public:
        Simple(int a, int b = 9){
            data1 = a;
            data2 = b;
        }
    
    void printData();
};

void Simple :: printData(void){
    cout << "The value of data is " << data1 << " & " << data2 << endl;
}

int main(){
    Simple s(1,4);
    s.printData();

    Simple p(3); //it will use default argument
    p.printData();

    return 0;
}