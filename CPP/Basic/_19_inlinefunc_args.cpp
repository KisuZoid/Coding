#include <iostream>
using namespace std;

//Inline func
inline int product(int a, int b){ // a function that is expanded in line when it is called. (in compile time) 
    return a*b;
}
//don't use inline function in case of recurssion, static variable, larger code block, loop or switch statement.

/*
# static variable

int product(int a, int b){
    static int c = 0; //this executes only once
    c = c+1; //next time this function is run, the value of c will be retained.
    return a*b+c;
}
*/

//Default arrgument
float moneyRecieved(int currentMoney, float factor=1.04){ //1.04 is the default value of factor 
    return currentMoney * factor;
}

//Constant arguments : don't want the value  to be modified or changed by the function.
/*
int sum(const int a, int b){

}
*/


int main(){
    //inline func
    int a, b;
    cout << "Enter the value of a and b ";
    cin >> a >> b;
    cout << "The product of a and b is " << product(a,b) << endl;

cout << endl;

    //arguments
    float money;
    cout << "Enter the amount of money in your account: ";
    cin >> money;
    cout << "If you have " << money << "rs in your back account, you will recieve " << moneyRecieved(money) << "rs after 1 year." << endl;
    cout << "If you are VIP and you have " << money << "rs in your back account, you will recieve " << moneyRecieved(money, 1.10) << "rs after 1 year." << endl;
    
    return 0;
}   