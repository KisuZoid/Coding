//Basic Structure of C++ program;
#include <iostream>
using namespace std;

int main()
{
    cout << "Hello, World\n";
    return 0;
}


//comment
/*
    comment
*/

/*
    iostream is a header file that helps input output. (it is inbuild library)
    "int main()" <datatype> main() { body } 
        main function is the body of your main code.
        int indicates that the main will return the interger value to the operating system after completing the program. 
            int is the integer datatype.
        return keyword indicate the value that main() function will return. 
        ";" means statement ends

        cout is a function the display to the screen.
            cout is in iostream file under namespace std.
            a << b; means b is assigned to a and then semi-colon ends that statement. 
            cout is the standard output function.
                //or
            we can use std::cout when we not consider using namespace std. 
*/