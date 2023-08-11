//3
//we can inventent our own data types.
#include <stdio.h>
#include "cs50.h"
#include <string.h>

typedef struct //typedef stands for define your own type, struct means it has a structure that you want to define.
{
    /* data */
    string name;
    string number;
}
person; //Word between outside the curly bracket and semicolon is the name of data type that we want to create.
//and the furnction of that data type is written inside the curly bracket.
//as soon as semi colon exicuted, every lines after that data type have acess to that data type here called person.
//name of a data type can be used for single variable or as an intire array. 

int main(void)
{
    person people[2]; //means in person data type there is array called people.

    people[0].name ="Kisu"; //in the data type, name data of the 0th array
    people[0].number = "1234";
    //people[0].name here "." indicated that going inside the array at people[0] in person memory and look at the name.

    people[1].name = "Kislay";
    people[1].number = "12345";

    string name = get_string("Name: ");
    for (int i = 0; i < 2; i++)
    {
        if (strcmp(people[i].name, name) == 0)
        {
            printf("Found %s\n", people[i].number);
            return 0;
        }
    }
    printf("Not found\n");
    return 1;
}