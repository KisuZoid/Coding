//5
#include "cs50.h"
#include <stdio.h>

void draw(int n);

int main(void)
{
    int height = get_int("Height: ");
    draw(height);
}

void draw(int n)
{
    if (n<=0)
    {
        return;
    }
    draw(n-1);

    for (int i = 0; i<n; i++)
    {
        printf("#");
    }
    printf("\n");


    //if height in draw(height) is 1 then printed out pyramid of 1 #, then 2 # then 3 # and so on...
    /*
    for (int i = 0; i < n; i++)
    {
        printf("#");
    }
    printf("\n");
    draw(n + 1);
    */ 
}