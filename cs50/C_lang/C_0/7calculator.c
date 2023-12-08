//7
#include <stdio.h>
#include "cs50.h"

//for more precise floating point values use *double* in place of *float* function {double itself suggest double the amount of bits are in use}
int main(void)
{
    long x = get_long("x: ");
    long y = get_long("y: ");

    double z = (double) x / (double) y;


    printf("%.20f\n",z);
}


//for no. with decimal points(floating point values)
/*
int main(void)
{
    long x = get_long("x: ");
    long y = get_long("y: ");

    float z = (float) x / (float) y;


    printf("%f\n",z);
}
*/
// printf("%.20f\n",z); gives result till 20 decimals but *float* function give precise answer till 7 decimals

//for operation of intergers
/*
int main(void)
{
    int x = get_int("x: ");
    int y = get_int("y: ");

    printf("%i\n", x+y );
}
*/

//for operating long integer(approx 2 billon)
/*
int main(void)
{
    long x = get_long("x: ");
    long y = get_long("y: ");

    printf("%li\n",x+y);
}
*/

/*
mathematical operation which is possible 

+ for additions
- for substractions
* for multiplication
/ is for division
% named as modulo is for reminder 
*/