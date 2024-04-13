#include <iostream>
#include <fstream>
using namespace std;

int main(){
    string read_txt;

    //Read txt from Sample_txt_02_File_IO_read.txt
    ifstream read("Sample_txt_02_File_IO_read.txt"); //read is the object of ifstream class.
    getline(read, read_txt); 
    cout << read_txt;

    return 0;
}

