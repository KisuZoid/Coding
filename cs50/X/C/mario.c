#include <stdio.h>
#include "cs50.h"

int main(void)
{
    //do while loop
    int n;//it is a deceleration that there is a integer n.
    do
    {
        n=get_int("length? ");
    }
    while (n<1);
//if value of n typed less than 1 then do  n=get_int("length? "); func. once again.

    int m;
    do
    {
        m=get_int("width? ");
    }
    while (m<1);

    for (int i=0; i<n; i++)
    {
        for (int j=0; j<m; j++)
        {
            printf("#");
        }
         printf("\n");
    }
}