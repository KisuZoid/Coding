#include <iostream>
using namespace std;

int main(){
    int age;
    cout<< "Your age: "<< endl;
    cin >> age;
    switch (age)
    {
    case 18:
        cout<<"Your age is 18";
        break;
    
    case 19:
        cout<<"Your age is 19";
        break;
    
    default:
        cout<< "No special case\n";
        break;
    }

    cout<<"this is switch case statement example";
    return 0;
}

/*
switch(variable)
{
    case (value of variable):
        //code block
        break; //break the switch case statement
    
    defaul:
        //this is deafult value of this statement if no case will match
        break;
}

//if break statement is not present then code gonna execute all the cases from top to bottom.
*/