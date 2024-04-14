#include <iostream>
using namespace std;

int main(){

}

/*
-->We can use constructor in derived class in C++
-->if base class constructor does not have any arguments, there is no need of any constructor in derived class.
--> But is there are one or more arguments in base class constructor, derived class need to pass arguments to the base class constructor.
--> if both base and derived class have constructors, base class constructor is executed first.
--> The constructor of derived class recieves all the arguments at once and then will pass the calls to respective base classes.
    ==>  derived(args1, args2, arga3, ...) : base1(args1, arg2), base2(arg3, arg4){...}
--> body willmcalled after all the constructors are finished executing.
--> the constructor of virtual base classes are invoked before an nonvirtual base class.

--> if there are multiple assignment then they will call in order they are declared from top to bottom, right to left.
*/