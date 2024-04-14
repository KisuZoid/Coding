#include <iostream>
using namespace std;

class Student{
    protected:
        int roll_no;
    public: 
        void set_number(int a){
            roll_no = a;
        }
        void print_number(void){
            cout << "Your roll number is " << roll_no << endl;
        }
};

class Test : virtual public Student{
    protected:
        float maths, physics;
    public:
        void set_marks(float m1, float m2){
            maths = m1;
            physics = m2;
        }
        void print_marks(void){
            cout<< "Your result is here: "<< endl
            << "Maths: " << maths << endl
            << "Physics: " << physics << endl;
        }
};

class Sport : virtual public Student{
    protected:
        float score;
    public:
        void set_score(float sc){
            score = sc;
        }
        void print_score(void){
            cout << "Your PT score is " << score << endl;
        }
};
//as roll_no is procted is base class, and test and score will both inherit roll_no --> it will generate ambiguity if "virtual is missing"

class Result : public Test, public Sport{
    private:
        float total;
    public:
        void display(void){
            total = maths + physics + score;
            print_number();
            print_marks(); 
            print_score();

            cout<<"Your total score is: " << total<<endl;
        }
};

int main(){
    Result kisu;
    kisu.set_number(16);
    kisu.set_marks(86, 94);
    kisu.set_score(85.9);
    kisu.display();
    return 0;
}

/*
derived1 <-- Base --> derived2 | derived1 --> derived3 <-- derived2 
==> it will may create duplicacy of variale and function for derived3. 
    --> so we use 'virtual' keyword to prevent duplicacy.

*/