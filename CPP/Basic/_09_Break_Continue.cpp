#include <iostream>
using namespace std;

int main(){
    for (int i = 0; i < 4; i++)
    {
        if(i==2){
            break; //means break out of the loop if i = 2;
        }
        cout<<i<<endl;
    }
    cout<<endl;
    for (int i = 0; i < 4; i++)
    {
        if (i==2)
        {
            continue; //means continue the loop without going further down.
                        //i.e. cout will not gonna print at 2, because it comes after condition.
                        //      condition will continue the next iteration, means 2 will gonna skip.
        }
        cout<<i<<endl;
    }

    return 0;
}