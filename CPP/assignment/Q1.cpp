// Create a fuction which takes 2 point objects and compute the distance between those points.
#include <iostream>
#include <cmath>
using namespace std;

class Point
{
    double a, b;

public:
    Point(double x, double y)
    {
        a = x;
        b = y;
    }

    void point(void)
    {
        cout << "The required point is (" << a << "," << b << ")" << endl;
    }
};

void distance(double X1, double Y1, double X2, double Y2)
{
    double X, Y, x1, x2, y1, y2, dist;
    x1 = X1;
    y1 = Y1;
    x2 = X2;
    y2 = Y2;

    X = (x2 - x1) * (x2 - x1);
    Y = (y2 - y1) * (y2 - y1);
    dist = sqrt(X + Y);
    cout << "The required distance between (" << x1 << "," << y1 << ") & (" << x2 << "," << y2 << ") is " << dist << endl;
}

int main()
{
    double num1, num2;
    cout << "X of First number: ";
    cin >> num1;
    cout << "Y of first number: ";
    cin >> num2;

    Point p1(num1, num2);
    p1.point();

    double num3, num4;
    cout << "X of second number: ";
    cin >> num3;
    cout << "Y of second number: ";
    cin >> num4;

    Point p2(num3, num4);
    p2.point();

    distance(num1, num2, num3, num4);

    return 0;
}