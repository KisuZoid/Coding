//11
#include <stdio.h>
#include "cs50.h"
#include <string.h>

int main(void)
{
    string name = get_string("What's your name? ");
     int n = strlen(name); //strlen stands for string length, and it is the part of string.h library 
     printf("%i\n",n);
}


/*
int main(void)
{
    string name = get_string("What's your name? ");

    int n = 0;
    while (name[n] != '\0') // != means not equal
    {
        n++;
    }
    printf("%i\n", n);
}
*/