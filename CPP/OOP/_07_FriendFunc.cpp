#include <iostream>
using namespace std;

class Complex{
    int a,b;

    public:
        void setNum(int n1, int n2){
            a = n1;
            b = n2;
        }

        void printNum(){
            cout << "your number is " << a << "+" << b << "i" << endl;
        }

        //for using private data of Complex class outside the class, sumComplex function have to be atleat friend func of this class.
        friend Complex sumComplex(Complex o1, Complex o2);
};

Complex sumComplex(Complex o1, Complex o2){
    Complex o3;
    o3.setNum((o1.a + o2.a), (o1.b + o2.b));
    return o3;  
}

int main(){
    Complex c1, c2, sum;

    c1.setNum(1,4);
    c1.printNum();
    
    c2.setNum(5,8);
    c2.printNum();

    sum = sumComplex(c1, c2);
    sum.printNum();
    return 0;
}

/*
//Properties of friend function
    1. Not in the scope of class
    2. since it is not in the scope of the class, it can't be called from the object of that class. c1.sumComplex() --> invalid
    3. can be invoked without the help of the object
    4. usually contains inside the public or private section of the class
    5. can be declared inside public or private section of the class.
    6. it cannot access the members directly by their names and need object_name.member_name to access any member.
*/