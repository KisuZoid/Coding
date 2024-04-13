/*
Create 2 classes:
    1. SimpleCalcculator - takes input of 2 numbers using utility function and perform +, -, *, /
    2. ScientificCalculator - Takes input of 2 numbers using a utility function and perform any four scientific operation of your choice

    --> and displays the result using another function.

    create another class HybridCalculator and inherit it using these 2 classes
*/

#include <iostream>
#include <cmath>
using namespace std;

class SimpleCalc
{
private:
    double num1, num2;
protected:
    void input1(double x, double y)
    {
        num1 = x;
        num2 = y;
    }
    void show_SimpleCalc(void);
};

void SimpleCalc :: show_SimpleCalc()
{
    cout << num1 << " + " << num2 << " = " << num1 + num2 << endl; 
    cout << num1 << " - " << num2 << " = " << num1 - num2 << endl; 
    cout << num1 << " * " << num2 << " = " << num1 * num2 << endl; 
    cout << num1 << " / " << num2 << " = " << num1 / num2 << endl; 
}

class ScientificCalc
{
private:
    double num1, num2;

protected:
    void input2(double x, double y)
    {
        num1 = x;
        num2 = y;
    }
    void show_ScientificCalc(void);
};

void ScientificCalc :: show_ScientificCalc()
{
    cout << "Sine of " << num1 << " is " << sin(num1) << " and " << num2 << " is " << sin(num2) << endl;
    cout << "Cosine of " << num1 << " is " << cos(num1) << " and " << num2 << " is " << cos(num2) << endl; 
    cout << "Tangent of " << num1 << " is " << tan(num1) << " and " << num2 << " is " << tan(num2) << endl; 
    cout << "Root of " << num1 << " is " << sqrt(num1) << " and " << num2 << " is " << sqrt(num2) << endl; 
}

class HybridCalculator : public SimpleCalc, public ScientificCalc
{
    public:
    void input()
    {
        double x, y;
        cout << "First Number: ";
        cin >> x;
        cout << "Second Number: ";
        cin >> y;
        input1(x, y);
        input2(x, y);
    }
    void result_SimpleCalc(void)
    {
        show_SimpleCalc();
    }
    void result_ScientificCalc(void)
    {
        show_ScientificCalc();
    }
};

int main()
{
    HybridCalculator calc;
    calc.input();

    calc.result_SimpleCalc();
    calc.result_ScientificCalc();
    return 0;
}