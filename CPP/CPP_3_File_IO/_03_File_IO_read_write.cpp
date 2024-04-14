#include <iostream>
#include <fstream>
using namespace std;

int main(){
    string write_txt, read_txt;

    ofstream write("./txt/Sample_03.txt");
    cout << "Enter your name: ";
    cin >> write_txt;
    write << "My name is " + write_txt;
    write.close(); //we are closing this write object of ofstream --> link between .txt/Sample_03.txt file and this cpp file is now close for writing.

    ifstream read("./txt/Sample_03.txt");
    getline(read, read_txt);
    cout << "The content of this file: "<< endl << read_txt;
    read.close();

    return 0;
}

//using close() func, we can read and write within same file.