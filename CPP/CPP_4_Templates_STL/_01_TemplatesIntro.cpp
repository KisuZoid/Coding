//important for compititive programming.
#include <iostream>
using namespace std;

int main(){
    
}

//Templates are also called as parameterised classes
/*
Why use templates:
    1. helps in DRY(do not repeat yourself) principal

Syntax: (it represent many classes)
template <class T>
class vector{
    T *arr;
    public:
        vector(T *arr)
        {
            //code block
        }
}

int main(){
    vector<int> myVec(ptr);
    vector<float> myVec(ptr);
}

// --> T can be int, float, char ect...
*/