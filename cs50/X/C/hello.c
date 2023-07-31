#include <stdio.h>
#include "cs50.h"

int main(void)
{
    string x = get_string("what is your first name? ");
    string y = get_string("what is your last name? ");
    float z = get_float("How much you got in 12th? ");
    printf("Hello, %s %s!\n %.2f%% is in your 12th\n", x, y, z);
}

