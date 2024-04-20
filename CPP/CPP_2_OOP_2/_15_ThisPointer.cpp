#include <iostream>
using namespace std;

class A{
    int a; //--> let a'
    public:

        A & setData(int a){ //--> let a"
            this -> a = a;
            return *this;
        }
//or
        /*
        void setData(int a){
                this -> a = a;  
            }
        */
// "this -> a" here "a" is a' variable and "a" after equal to sign is a" variable.

// "this" is a keyword which is a pointer which points to the object which invokes the member function.

        void getData(){
            cout << "The value of a is " << a << endl;
        }
};

int main(){
    A a;
    a.setData(1);
    a.getData();

    return 0;
}


/* --> this will generate garbage value for 'a'.
class A{
    int a;
    public:
        void setData(int a){
            a = a;
        }

        void getData(){
            cout << "The value of a is " << a << endl;
        }
};

int main(){
    A a;
    a.setData(1);
    a.getData();

    return 0;
}
*/