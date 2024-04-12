#include <iostream>
#include <string>
using namespace std;

//Nesting of member function
class Binary{
    string s; //class members are private by default
    void chk_bin(void);

    public:
        void read(void);
        void onesCompliment(void);
        void display(void);
};

void Binary :: read(void){
    cout << "Enter a binary number" << endl;
    cin>>s;
    //nesting of member
    chk_bin();
}

void Binary :: chk_bin(void){
    for (int i = 0; i < s.length(); i++)
    {
        if (s.at(i) != '0' && s.at(i) != '1'){
            cout << "Incorrect binary format" << endl;
            exit(0);
        }
    }
}

void Binary :: onesCompliment(void){
    for (int i = 0; i < s.length(); i++){
            if (s.at(i) == '0'){
                s.at(i) = '1';
            }
            else{
                s.at(i) = '0';
            }
    }
}

void Binary :: display(void){
    cout << "Display Binary number after compliment "<< endl;
    for (int i =0; i < s.length(); i++)
    {
        cout << s.at(i);
    }
}

int main(){
    Binary b;
    b.read();
    b.onesCompliment();
    b.display();
    return 0;
}