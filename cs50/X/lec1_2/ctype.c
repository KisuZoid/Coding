#include <stdio.h>
#include "cs50.h"
#include <string.h>

int main(void)
{
    string s = get_string("Before: ");
    printf("After: ");

    for (int i = 0; i < strlen(s); i++)
    {
        //this is how do i check something is in lower case and force it to be in upper case.
        if (s[i] >= 'a' && s[i] <= 'z') // means lower case a to z characters in array of string s | && represents and
        {
            printf("%c", s[i] - 32);//%c denotes array of all characters in string s[i] - 32
            //as char is just a number inside, so we can do arthematic on it. 
            //as for lower case ascii assigned the numerical value from 97 to 122 and for upper case 65 to 90. example for a : 97 and A : 65 difference is of 32 , this is same difference for the respective characters, prefer ascii.
        }
        else
        {
            printf("%c", s[i]);
        }
    }
    printf("\n");
}