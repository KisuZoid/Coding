#include <stdio.h>
#include "cs50.h"

//array : a method of clubbing multiple entities of similar tyoe into a large group.

int N;//N is mentioned in top of all and not in any specified bracket means it is valid(defined) for all functions below. 

float average(int length, int num[]);
//num is a variable name here & [] this bracket indicate that input is array of int | average is assigned function whose input is in integer and out is in float

int main(void)
{
    int N = get_int("Enter Number of scores want to average? ");
    int scores[N]; // means a array called scores of size N(N in number) which is in integer
    for(int i=0; i<N; i++)
    {
        scores[i]=get_int("Scores: ");
    }
    printf("Average: %.2f\n", average(N, scores)); //N resembels with length and scores resembels with num.
}

//for function average() ; 1st input of this function denotes vasriable length and second denotes array called num here, and both are integer.
float average(int length, int num[])
{
   int sum=0; //initial value of variable sum is 0
   for(int i=0; i<length; i++)
   {
    sum += num[i]; // we can also use sum = sum + num[i];
   }
   return sum/(float)length;//return function returns that value to the average() function
}




/*
int main(void)
{
    int scores[3];
    for (int i=0; i<3; i++)
    {
        scores[i]=get_int("Scores: ");
    }
    printf("Average: %f\n",(scores[0]+scores[1]+scores[2]) / (float) 3); //we can write (float) 3 or 3.0 coz both are floating point value.
}
*/

/*
int main(void)
{
    int scores[3];
    scores[0] = 72;
    scores[1] = 73;
    scores[2] = 33;

    printf("Average: %f\n", (scores[0] + scores[1] + scores[2]) / (float)3);
}
*/



/*
bool : 1 byte
int : 4 bytes
long : 8 bytes
float : 4 bytes
double : 8 bytes
char : 1 byte
string : ? bytes (? means depends upon size of string)
*/