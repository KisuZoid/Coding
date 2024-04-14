#include <iostream>
using namespace std;

class ShopItem{
    int id;
    float price;

    public:
        void setData(int a, float b){
            id = a;
            price = b;
        }
        void getData(void){
            cout << "Code of this item is " << id << endl;
            cout << "Price of this item is " << price << endl;
        }
};

int main(){
    //Array of object
    int size = 3;
    ShopItem *ptr = new ShopItem[size];

    ShopItem *ptrTemp = ptr; //for proper execution. 

    int p, q, i;
    for (i = 0; i < size; i++){
        cout << "Enter ID and price of item " << i+1 << endl;
        cin >> p >> q;
        ptr -> setData(p, q);
        ptr++;
    }

    for (i = 0; i < size; i++){
        cout << "Item number " << i+1 << endl;
        ptrTemp -> getData();
        ptrTemp++;
    }
    return 0;
}

// int *ptr = new int[34]; --> allocate memory to store 34 integer value dinamically, and store the address of 1st memory to ptr. and using increment in ptr, we will get the rest of the values.