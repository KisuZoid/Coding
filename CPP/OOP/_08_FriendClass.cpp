#include <iostream>
using namespace std;

//forward declaration: this will may be present forward in our code.
class Complex;

class Calculator{
    public:
        int add (int a, int b){
            return (a+b);
        }

        int sumRealComplex(Complex, Complex);
        int sumImgComplex(Complex, Complex);
};

class Complex{
    int a,b;
    //Individually declaration of function as friend 
    /*
    friend int Calculator :: sumRealComplex(Complex o1, Complex o2); //giving access to use private data set of Complex class to sumRealComplex() func of Calculator class.
    friend int Calculator :: sumImgComplex(Complex o1, Complex o2);
    */

    //Aliter: Declare the entire calculator class as friend --> so that no need to declare function by function
    friend class Calculator;
    
    public:
        void setNum(int n1, int n2){
            a = n1;
            b = n2;
        }

        void printNum(){
            cout << "your number is " << a << "+" << b << "i" << endl;
        }
};

int Calculator :: sumRealComplex(Complex o1, Complex o2){
    return(o1.a + o2.a);
}

int Calculator :: sumImgComplex(Complex o1, Complex o2){
    return(o1.b + o2.b);
}


int main(){
    Complex o1, o2;

    o1.setNum(1,4);
    o2.setNum(5,7);

    Calculator calc;
    int valueReal = calc.sumRealComplex(o1, o2);
    int valueImg = calc.sumImgComplex(o1, o2);

    cout << "Sum of real part of o1 and o2 " <<  valueReal << endl;
    cout << "Sum of imagiary part of o1 and o2 " <<  valueImg << endl;

    return 0;
}