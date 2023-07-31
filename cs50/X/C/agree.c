#include <stdio.h>
#include "cs50.h"

int main(void)
{
    char c = get_char("do you agree? ");

    if (c == 'y' || c == 'Y')
    {
        printf("Agreed. \n");
    }
    if (c == 'n' || c == 'N')
    {
        printf("Not agreed. \n");
    }
}