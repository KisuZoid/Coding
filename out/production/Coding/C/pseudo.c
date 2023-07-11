//extention of mario
#include <stdio.h>
#include "cs50.h"

//give own functional library key's header with semi colon here to indicate C that these function are mentioned
int get_size(void);
void print_grid(int size);

int main(void)
{
    //Pseudocode and own library functional key

    //get size of grid in mario
    int k = get_size();

    //get grid of bricks(#) in mario
    print_grid(k);
}


int get_size(void)
{
    int n;
    do
    {
        n = get_int("size: ");
    }
    while(n<1);
    return n;
}

void print_grid(int size)
{
    for (int i=0; i < size; i++ )
    {
        for (int j=0; j<size; j++)
        {
            printf("#");
        }
        printf("\n");
    }
}

