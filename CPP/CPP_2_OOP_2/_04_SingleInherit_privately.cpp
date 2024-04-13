#include <iostream>
using namespace std;

class Base
{
    int data1; // private by default and it can't be inherited directly
public:
    int data2;
    void setData();
    int getData1();
    int getData2();
};

void Base ::setData(void)
{
    data1 = 10;
    data2 = 20;
}

int Base ::getData1(void)
{
    return data1;
}

int Base ::getData2(void)
{
    return data2;
}

// class is being derived
class Derived : private Base
{
    int data3;

public:
    void process();
    void display();
};

// for using private member of base class, we can use public member function of base class.
void Derived ::process()
{
    setData(); // additional change

    data3 = data2 * getData1();
}

void Derived ::display()
{
    cout << "The value of data1 is " << getData1() << endl;
    cout << "The value of data2 is " << data2 << endl;
    cout << "The value of data3 is " << data3 << endl;
}

int main()
{
    Derived der;
    // der.setData(); --> we can't use this, as derived class is inherited privately.
    der.process();
    der.display();
    return 0;
}