#include <iostream>
#include <fstream>
using namespace std;

int main(){
    string print_01_out = "Sample for print inside sample_01.txt file side folder txt";
    string read_01_in;

    //Opening files using constructor and writing it.
    ofstream out("./txt/sample_01_File_IO_out.txt"); //write operation
    out << print_01_out;

    ifstream in("./txt/sample_01_File_IO_in.txt"); //read operation
    // in >> read_01_in; //--> this will give just first word only, 

    //to get whole line:
    getline(in, read_01_in);
    cout << read_01_in;
    return 0;
}

/*
The useful classes for working with files in c++ are :
    1. fstreambase
    2. ifstream --> derived from fstreambase
    3. ofstream --> derived from fstreambase
*/

/*
In order to work with files in C++, you will have to open it, primarily, there are 2 ways to open a file:
    1. Using the constructor
    2. Using the member function open() of the class
*/

/*
./ --> means in same folder
../ --> means one folder back

./txt --> inside txt file of same folder you are in.
*/