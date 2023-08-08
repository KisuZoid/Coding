//1
#include <stdio.h>
#include "cs50.h"
#include <string.h>

int main(void) //linear search
{
    string strings[] = {"battleship", "boot", "cannon", "iron", "thimble", "top hat"};

    string s = get_string("String: ");
    for (int i = 0; i<6; i++)
    {
        if (strcmp(strings[i], s) == 0) // means does the return value of a function strcmp(stands for string compare) is 0 when pass in current string and that the user input.
        {
            printf("Found\n");
            return 0;
        }
    }
    printf("Not found\n");
    return 1;
}




/*
int main(void) //linear search
{
    int numbers[] = {20, 500, 10, 5, 100, 1, 50}; //static array, array that never changes.
    //means give an array whatever the size of bracket and containing the values in it.

    //or 
    
    #int number[7];
    #numbers[0] = 20;
    #numbers[1] = 500;
    #numbers[2] = 10;
    #numbers[3] = 5;
    #numbers[4] = 100;
    #numbers[5] = 1;
    #numbers[6] = 50;
    

   int n = get_int("Number: "); 
   for (int i = 0; i<7; i++)
        {
            if (numbers[i]==n)
            {
                printf("Found\n");
                return 0;
            }
        }
        printf("Not found\n");
        return 1;
}
*/