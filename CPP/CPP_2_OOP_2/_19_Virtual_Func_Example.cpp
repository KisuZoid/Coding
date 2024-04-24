#include <iostream>
#include <cstring>
using namespace std;

class Tutorial{
    protected:
        string title;
        float rating;
    public:
        Tutorial(string s, float r){
            title = s;
            rating = r;
        }
        virtual void display(){ cout << "kisu";} //if code doesn't find another display() function, then it will run this base class display() i.e. print kisu.
};

class TutorialVideo : public Tutorial{
    float videoLength;
    public:
        TutorialVideo(string s, float r, float vl) : Tutorial(s, r){
            videoLength = vl;
        }
        void display(){
            cout << "This is an amazing video with title "<< title << endl;
            cout << "Ratings: " << rating << " out of 5 stars"<< endl;
            cout << "Length of this video is " << videoLength << " minutes" << endl;
        }
};

class TutorialText : public Tutorial{
    int words;
    public:
        TutorialText(string s, float r, int wc) : Tutorial(s, r){
            words = wc;
        }
        void display(){
            cout << "This is an amazing text with title "<< title << endl;
            cout << "Ratings of this text tutorial: " << rating << " out of 5 stars"<< endl;
            cout << "Number of words in this text tutorial is: " << words << " words" << endl;
        }
};

int main(){
    string title;
    float rating, vlen;
    int words;

    //For tutorial video
    title = "CPP tutorial";
    vlen = 4.56;
    rating = 4.89;
    TutorialVideo tutVideo(title, rating, vlen);
    tutVideo.display();

cout << endl;

    //For tutorial text
    title = "CPP text tutorial";
    words = 456;
    rating = 4.89;
    TutorialText tutText(title, rating, words);
    tutText.display();

cout << endl;

    Tutorial * tuts[2];
    tuts[0] = &tutVideo;
    tuts[1] = &tutText;

    tuts[0]->display();
    tuts[1]->display();

    return 0;
}

/*
Rules for virtual function:
    1. the can't be static
    2. they are accessed by object pointers
    3. virtual function can be a friend of another class
    4. a virtual function in base class can might not be used
    5. if a virtual function is defined in a base class, then there is no necessity to redefine it in a derived classes.  
*/