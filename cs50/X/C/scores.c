#include <stdio.h>
#include "cs50.h"

const int N=3;

float average(int length, int num[]);
//num is a variable name here & [] this bracket indicate that input is array of int | average is assigned function whose input is in integer and out is in float

int main(void)
{
    int scores[N];
    for(int i=0; i<N; i++)
    {
        scores[i]=get_int("Scores: ");
    }
    printf("Average: %f\n", average(N, scores));
}

//lenght is using for more specification.
float average(int length, int num[])
{
   int sum=0; //initial value of variable sum is 0
   for(int i=0; i<length; i++)
   {
    sum += num[i]; // we can also use sum = sum + num[i];
   }
   return sum/(float)length;
}




/*int main(void)
{
    int scores[3];
    for (int i=0; i<3; i++)
    {
        scores[i]=get_int("Scores: ");
    }
    printf("Average: %f\n",(scores[0]+scores[1]+scores[2]) / (float) 3);
}*/