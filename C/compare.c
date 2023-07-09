#include <stdio.h>
#include "cs50.h"

int main(void)
{
    int x = get_int("what is your x?\n");
    int y = get_int("what is your y?\n");

    if (x<y)
    {
        printf("x is less than y\n");
    }
    else if (x>y)
    {
        printf("x is greater than y\n");
    }
    else
    {
        printf("x is equal to y\n");
    }
}