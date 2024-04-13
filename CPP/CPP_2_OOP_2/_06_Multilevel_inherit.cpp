#include <iostream>
using namespace std;

class Student
{
protected:
    int roll_number;

public:
    void set_roll_number(int);
    void get_roll_number(void);
};

void Student ::set_roll_number(int r)
{
    roll_number = r;
}

void Student ::get_roll_number()
{
    cout << "Your roll number is " << roll_number << endl;
}

class Exam : public Student
{
protected:
    float maths;
    float physics;

public:
    void set_marks(float, float);
    void get_marks(void);
};

void Exam ::set_marks(float m1, float m2)
{
    maths = m1;
    physics = m2;
}

void Exam ::get_marks(void)
{
    cout << "The marks obtains in maths are: " << maths << endl;
    cout << "The marks obtains in physics are: " << physics << endl;
}

class Result : public Exam
{
    float percentage;

public:
    void display()
    {
        get_roll_number();
        get_marks();
        cout << "Your percentage is " << (maths + physics) / 2 << endl;
    }
};

int main()
{
    Result kisu;
    kisu.set_roll_number(16);
    kisu.set_marks(86, 94);

    kisu.display();
    return 0;
}

/*
Notes:
    If we are inheriting B from A and C from B: [A-->B-->C]
        1. A is the base class for B and B is the base class for C
        2. A-->B-->C : this is call inheritance path
*/