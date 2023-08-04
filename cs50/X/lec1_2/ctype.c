#include <stdio.h>
#include "cs50.h"
#include <string.h>
#include <ctype.h>

int main(void)
{
    string s = get_string("Before: ");
    printf("After: ");

    for (int i = 0, n = strlen(s); i < n; i++) //this little decleration of n makes program faster coz length is defined so that computer has no need to check length of string each time for i < n.
    {
        //this is how do i check something is in lower case and force it to be in upper case.
            printf("%c", toupper(s[i]));//toupper takes character as input and just make it uppercase i.e it does the math itself.
    }
    printf("\n");
}



/*
int main(void)
{
    string s = get_string("Before: ");
    printf("After: ");

    for (int i = 0; i < strlen(s); i++)
    {
        //this is how do i check something is in lower case and force it to be in upper case.
        if (islower(s[i])) //islower & toupper is the ctype library thing
        {
            printf("%c", toupper(s[i]));//toupper takes character as input and just make it uppercase i.e it does the math itself.
        }
        else
        {
            printf("%c", s[i]);
        }
    }
    printf("\n");
}
*/




/*
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
*/