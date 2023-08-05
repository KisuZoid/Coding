#include <stdio.h>
#include "cs50.h"

int main(void)
{
    string x = get_string("what is your first name? ");
    string y = get_string("what is your last name? ");
    float z = get_float("How much you got in 12th? ");
    printf("Hello, %s %s!\n%.2f%% is in your 12th\n", x, y, z);
    // %% is a way to show % sign in output.
    //first %s denotes x (here x must be string), second %s denotes y(y must be strings), %f denotes z(z must be float). space between (%s %s) means in output there will be a space  between values of x and y.
    //%.2f means output as float till 2 decimal places
}

/*
* ; is should be after all statement
*here we include cs50 library coz some keywords are part of cs50 itself. and there is inbuild library of C as well "stdio"
*string x means x is a string(Sequence of characters), float z means z is floating point value, int k means k is integer
*float means decimal values
*get_float or get_string is functions that takes input from user in float or string formate respectively.
*x,y,z are variable resembeles with correspponding values that realed with (=) sign.
*printf output type function. whatever written in " " (double quotes)  are gonna print.
*%s s is for string, %f is for float, %i or %d is for integer.  
* \n makes new line.
*in printf(" ") function,space between quotes gives space in output   
*/