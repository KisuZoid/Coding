//play with string
#include <iostream>
#include <string>
using namespace std;

int main(){
    string input;

    cout << "Write the word: ";
    cin >> input;

    cout << "Number of alphabets in input: " << input.length() << endl;

    for (int i= 0; i < input.length(); i++){
        cout << input.at(i);
    }
    cout<< endl;

    for (int i = input.length()-1; i >= 0 ; i--){ //length() is starts from 1st index
        cout << input.at(i); //at() is zero indexed
    }
    cout<< endl;

    cout << "Append Anand after input kislay: " << input.append(" Anand") << endl;


    input.clear(); //clear the input
    return 0;
}