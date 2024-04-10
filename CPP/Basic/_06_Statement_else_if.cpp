#include <iostream>
using namespace std;

int main(){
    int age;
    cout << "Tell me your age: "<< endl;
    cin >> age;

    if((age > 18) && (age > 0)){
        cout << "You are eligible to vote in india." << endl;
    }
    else if(age == 18){
        cout << "Your Name is added to voter list, \n Now you can vote" << endl; 
    }
    else if(age < 0){
        cout << "you are not yet born";
    }
    else{
        cout << "You can't vote";
    }
    return 0;
}

/*
if (condition 1){
    execute this if condition 1 is true and break from statements
}
else if (condition 2){
    (jump to this block of code if and only if upper one is false)
    execute this if condition 2 is true and break from statement 
}
else{
    if all the condition are false then execute this
}
*/