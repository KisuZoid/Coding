#include <iostream>
using namespace std;

class Y; //forward declaration of Y because add function contain Y as well.

class X{
    int data;

    public:
        void setValue(int value){
            data = value;
        }

    friend void add(X, Y);
};

class Y{
    int num;

    public:
        void setValue(int value){
            num = value;
        }
    
    friend void add(X, Y);
};

void add(X o1, Y o2){
    cout << "Summing the data of X and Y gives me " << o1.data + o2.num ;
}

int main(){
    X a1;
    Y b1;

    a1.setValue(5);
    b1.setValue(6);

    add(a1, b1);

    return 0;
}