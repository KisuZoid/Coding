#include <iostream>
using namespace std;

struct student
{
    /* data */
    int eID;
    char grade;
    float marks;
};

typedef struct artist
{
    int eID;
    int Number_of_Art;
} art; //we can use "art" to call this struct.


int main(){
    struct student kisu; //kisu is a variable name for struct student data type.
    struct student kislay;
    art kisuzoid;

    kisu.eID = 1;
    kisu.grade = 'A';
    kisu.marks = 95.6;

    kislay.eID = 2;
    kislay.grade = 'A';
    kislay.marks = 92.6;

    kisuzoid.eID = 1;
    kisuzoid.Number_of_Art = 5;

    cout << "The eID of 'Kisu' is "<< kisu.eID << endl;
    cout << "The grade of 'Kisu' is "<< kisu.grade << endl;
    cout << "The marks of 'Kisu' is "<< kisu.marks << endl;

cout<<endl;

    cout << "The eID of 'kislay' is "<< kislay.eID << endl;
    cout << "The grade of 'kislay' is "<< kislay.grade << endl;
    cout << "The marks of 'kislay' is "<< kislay.marks << endl;

cout << endl;

    cout << "The eID of 'kisuzoid' is "<< kisuzoid.eID << endl;
    cout << "The Number of art by 'kisuzoid' is "<< kisuzoid.Number_of_Art << endl;

    return 0;
}

//struct(structure) is the user defined data type, and used to combine different data types.