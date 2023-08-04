#include "cs50.h"
#include <stdio.h>

int main(int argc, string argv[])
//main always returns integer value so we use int, and main means our main code line.
//main return 0 as an integer and 0 by default means success and it is always their automatically as a default value.
{
    if (argc != 2)
    {
        printf("Missing command_line argument\n");
        return 1; //means if this runs, then main will give 1 as int.
    }
    else
    {
        printf("Hello, %s\n", argv[1]);
        return 0; //and if this will run then main will give 0 as int.
    }
}

//for getting int result of main, use " echo $? " in command line this gives exit status of the program