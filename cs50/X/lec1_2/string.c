#include <stdio.h>
#include "cs50.h"

int main(void)
{
string words[2];

words[0] = "HI!";
words[1] = "BYE!";

printf("%s\n", words[0]);
printf("%s\n", words[1]);
printf("%c %c %c\n", words[0][0], words[0][1], words[0][2]);
printf("%c %c %c %c\n", words[1][0], words[1][1], words[1][2], words[1][3]);
}
//word[0][0] means word[0] is the name of array called word with 1st value of array i.e. [0] means HI!, 2nd [0] indicated the 1st character of the variable/array words[0]


/*
int main(void)
{
   string s = "HI!";

   printf("%s\n", s);
   printf("%c %c %c\n", s[0], s[1], s[2]);//using this we can treat string as a character so, use char. coz array of characters is string.
}
*/