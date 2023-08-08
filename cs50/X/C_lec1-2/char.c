//9
#include <stdio.h>
#include "cs50.h"

int main(void)
{
    char c1 = 'H';
    char c2 = 'I';
    char c3 = '!';
    string s = "HI!";
    char c4 = 'H';

    printf("%c%c%c\n%s\n%i", c1, c2, c3, s, c4); //%c denotes char
    //here c4 is a char that shows single character.
    // As character is just a number and string are just a array of characters for computer  so, %i will show the numerical value of c4(i.e H) here.
}



// char keyword stires single character and it use 1 byte for each char.
//char c1 = 'H'; char is written in single quotes. here c1 is the variable name of char keyword.

//string are just array/list of characters 
// string s = "Hi!" it takes 4(3 + 1) bytes total, 1 for each character and 1 extra \0 means closing of string.
//s[0] means H, s[1] means i, s[2] means !,s[3] means \0.

//in case of integer, let 72, 73, 33
//s[0] is 72, s[1] is 73, s[2] is 33, s[3] is 0(means stop the string)
// NUL is all zero bits, i.e. \0