//4
#include <stdio.h>
#include "cs50.h"

int main(void)
{
  //for loop
  for (int i=0; i<3; i ++)
  {
    printf("meow\n");
  }
  //initial value of variable i is 0; i is less than 3;
  // i = i+1 or i += 1 or i ++ all will increase i by 1 from minimum value (0 here) and continue increasing by 1 in each loop till the maximum value(3 here) of i.
}

//or 

/*
int main(void)
{
  int i = 3; 

  //while loop
  while(i > 0) 
  {
    printf("meow\n");
    i --;
  }
  //carry on the loop till i is greater than 0, initial value of i is 3, and value decreases by 1 due to i--; statement
}
*/

//or 

/*
int main(void)
{
  int i = 0; 

  //while loop
  while(i < 3)
  {
    printf("meow\n");
    i ++;
  }
}
*/




//to break infinite loop use ctrl + c key.
//for using inbuilt C library for boolean(1 or 0 i.e true or false) value, include <stdbool.h> library in top of the file. by the way cs50 library include bool values as well

//infinite loop
/*
int main(void)
{
  int i;

  while(1)
  {
    printf("meow\n");
  }
  // 1 means true condition i.e when program runs.
}
*/

//or

/*
int main(void)
{
  int i;

  while(true)
  {
    printf("meow\n");
  }
  // true means true condition i.e when program runs.
}
*/