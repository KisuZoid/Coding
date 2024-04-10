#include <iostream>
using namespace std;

int main(){
    //print 0123

    //for loop
    for (int i = 0; i < 4; i++)
    {
        cout<<i;
    }

   //do-while loop
   /*
   int i=0;
    do{
        cout << i;
        i++;
    }while(i<4);
   */

   //while loop
   /*
   int i = 0;
   while (i<4)
   {
    cout << i;
    i++;
   }
   */
   

    return 0;
}

/*loops in C++
    1. For loop
    2. While loop
    3. Do-While loop

    if condition will be always true then it becomes infinite loop. 
*/

/*
for(initialization; condition; updation)
{
    loop body(c++ code);
}

value is set as initialization, till condition is true, for loop will gonna run,
    and after each loop, updation will made.
*/

/*
while(condition){
    //code block
}

loop will run till conditon will true
*/

/*
do{
    //block of code
}while(condition);

execute atleast once, then check condition.
    loop the process till conditoin is true.
*/