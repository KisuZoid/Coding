#include <stdio.h>
#include "cs50.h"

int main(void)
{
    string x=get_string("what is your first name? ");
    string y=get_string("what is your last name? ");
    int z=get_int("How much you got in 12th? ");
    printf("hello, %s %s!\n %i%% is in your 12th\n", x, y, z);
}