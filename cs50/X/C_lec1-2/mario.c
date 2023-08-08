//5
#include <stdio.h>
#include "cs50.h"

int main(void)
{
    //do while loop
    int n; //declare that n is integeral variable
    do
    {
        n=get_int("length? ");
    }
    while (n<1);
//if value of n typed less than 1 then do  n=get_int("length? "); function once again.
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

/*
both are same:

int n=get_int("length? ");
    while(n<1)
    {
        n=get_int("length? ");
    }
    

int n;
    do
    {
        n=get_int("length? ");
    }
    while (n<1)
*/

/*
int main(void)
{
    const int n=3;

    for (int i=0; i<n; i++)
    {
        for (int j=0; j<4; j++)
        {
            printf("#");
        }
        printf("\n");
    }

    output : ####
             ####
             ####

//const means constant, const int n = 3; means we fix the value of n as 3, no matter what further the value of n will be assign in program set(parentheses), n always be 3 for that program set.
}
*/