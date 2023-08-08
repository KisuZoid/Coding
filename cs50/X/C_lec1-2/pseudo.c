//6
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
    return n; //return shows returning the value to the function.
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

/*
int get_size(void) 

here "int" represents that this is a integer function i.e. return is in integer.
as function do to not take any input so,we right keyword in side parentheses "void" that itself meaning void i.e nothing. this function only perform that is mentioned in "{ }"

and functionality of the function is in parentheses"{ }".
*/

/*
void print_grid(int size)

here it is just a print function that print whatever be the input(int/string/float etc.). it has no return value(not return any value to the function) so, we write void. 
void here represents the function type i.e it returns noting.

(int size) here int represents taken input type for the function i.e. integer type input and size is the name of variable of that input.
and functionality of the function is mentioned in "{ }"
*/