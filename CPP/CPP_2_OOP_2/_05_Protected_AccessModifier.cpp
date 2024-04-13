#include <iostream>
using namespace std;

class Base{
    private:
        int b;
    
    protected:
        int a;

};

class Derived : protected Base{

};

int main(){
    Base base;
    Derived der;
    // cout << der.a; --> will not work since a is protected in both base as well as derived class.
    return 0;
}

/*
for a protected member:
                        public derived  protected derived   private derived      
    1. private member   Not Inherited   Not Inherited       Not Inherited
    2. Protected member Protected       Protected           Private             
    3. Public member    Public          Protected           Private
*/