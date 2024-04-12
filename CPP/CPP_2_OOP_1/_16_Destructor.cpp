#include <iostream>
using namespace std;

int count = 0; //global variable

class Num{
    public:
        Num(){
            count++;
            cout << "This is the time when constructor is called for object number " << count << endl;
        }

        //Destructor
        ~Num(){
            cout << "This is the time when destructor is called for object number " << count << endl;
            count--;
        }
};

int main(){
    cout << "we are inside our main function " << endl;
    cout << "Creating first object n1" << endl;

    Num n1;
    {
        cout << "Entering this block" << endl;
        cout << "Creating two more objects" << endl;
        Num n2, n3;
        cout << "Exiting this block"<< endl;
    }
    cout << "Back to main"<< endl;
    return 0;
}

//Destructor will free up the memory occupied by constructors and objects.

//Destructor never taeks an argument nor does it return any value.

//when we will exiting the block, destructor will automatically called to free up memory.