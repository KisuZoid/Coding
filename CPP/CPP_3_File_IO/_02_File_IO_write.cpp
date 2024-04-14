#include <iostream>
#include <fstream>
using namespace std;

int main()
{
    string write_txt;

    //Open and Write txt from Sample_txt_02_File_IO_write.txt
    write_txt = "This is a sample txt file inside same folder for  write.";
    ofstream write("Sample_txt_02_File_IO_write.txt"); //write is the object for ofstream class.
    write << write_txt;

    return 0;
}