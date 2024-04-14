#include <iostream>
using namespace std;

class Complex{
    int real, img;
    public:
        void getData(){
            cout<<"The real part is " << real << endl;
            cout << "The imaginary part is " << img << endl;
        }

        void setData(int a, int b){
            real = a;
            img = b;
        }
};

int main(){
    /*
    Complex c1;
    Complex *ptr = &c1;
    */
//or
    Complex *ptr = new Complex;

    //using arrow operator
    ptr -> setData(1,54); //exactly same as (*ptr).setData(1, 54); 
    (*ptr).getData(); // --> same as c1.getData();
    
    return 0;
}
//*ptr is same value as c1, and ptr is same as address of c1.
//new complex will create new object dinamically