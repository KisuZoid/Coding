#include <iostream>
using namespace std;

int main(){
    enum Meal{breakfast, lunch, dinner};
    Meal m1 = breakfast;
    cout << m1 << endl;
    cout << lunch << endl;
    cout << dinner;
    return 0;
}