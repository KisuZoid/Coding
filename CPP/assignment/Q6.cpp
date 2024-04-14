//Triangl using class and private data set for length.
#include <iostream>
using namespace std;

class Triangle{
private:
    int s1, s2, s3;
public:
    void set_side(void);
    void triangle(void);

    
    void result(void){
        if ((s1 + s2 > s3) && (s1 + s3 > s2) && (s2 + s3 > s1)){
            triangle();
        }
        else{
            cout << "Not a triangle" << endl;
        }
    }
};

void Triangle :: set_side(void){
    int a, b, c;
    cout << "Enter length of sides of triangle(s1, s2, s3): " << endl;
    cin >> a >> b >> c;
    s1 = a;
    s2 = b;
    s3 = c;
}

void Triangle :: triangle(){
    if ((s1 == s2) && (s1 == s3)){
        cout << "Equilateral Triangle";
    }
    else if ((s1 == s2) || (s1 == s3) || (s2 == s3)){
        cout << "Isoceles Triangle";
    }
    else{
        cout << "Scalar Triangle";
    }
}

int main(){
    Triangle tri;
    tri.set_side();
    tri.result();
    return 0;
}