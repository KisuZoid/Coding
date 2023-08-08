//13
//this is how we use command line input direct into our code.
#include <stdio.h>
#include "cs50.h"

int main(int argc, string argv[])
{
    if (argc == 3) //== means equals to 
    //argc is equal to 3 means argument count is 3 , one for argv[1], one for argv[2], and one for world 
    {
        printf("Hello, %s %s\n", argv[1], argv[2]);
    } 
    else
    {
        printf("Hello, world");
    }
}



/*
//int main(void)  as in main() by using void, it is declared that it does not take any command line arguments.

int main(int argc, string argv[])//now main will take command line argument anyhow.
{
    printf("hello, %s %s\n", argv[1], argv[2]);
}

//int argc means argument count is in integer format
//string argv[] it is array of string that we type in prompt or command line.
*/