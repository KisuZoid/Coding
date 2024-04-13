#include <iostream>
#include <fstream>
#include <string>
using namespace std;

int main(){
    ofstream out;
    out.open("./txt/Sample_04.txt");
    out << "This is me. \n";
    out << "This is also me.";
    out.close();

    /*
    ifstream in;
    string st, st1, st2;
    in.open("./txt/Sample_04.txt");
    in >> st >> st1 >> st2;
    cout << st << st1 << st2; // --> print Thisisme. --> This <-- st, is <-- st1, me. <-- st2
    in.close();
    */
    
    //Aliter, using loop
    ifstream in;
    string st;
    in.open("./txt/Sample_04.txt");
    while(in.eof() == 0){ //eof --> end of file, eof==0 means not encountered end of line.
        getline(in, st); //getline() --> part of string library
        cout << st << endl;
    }
    in.close();
    

    return 0;
}