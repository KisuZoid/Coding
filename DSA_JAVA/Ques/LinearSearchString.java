package Ques;

import java.util.Arrays;

public class LinearSearchString {

    public static void main(String[] args){
    //Character in the name
    //Kislay : find s exist in kislay?
    String name = "Kislay";
    char Target = 's';
    System.out.println(search(name, Target));

    System.out.println(Arrays.toString(name.toCharArray()));
    //Arrays : This class contains various methods for manipulating arrays (such as sorting and searching).
    //toString() : Returns a string representation of the contents of the specified array.
    //toCharArray() : Converts string to a new character array.
    System.out.println(search2(name, Target));
    }

    //Searching using for loop
    static boolean search(String name, char target){
        if (name.length()==0){
            return false;
        }

        for (int i=0; i < name.length(); i++){
            if (name.charAt(i) == target){
                return true;
            }
        }
        return false;
    }
    
    //Searching using for each loop
    static boolean search2(String name, char target){
        if (name.length()==0){
            return false;
        }

        for (char ch : name.toCharArray()){ //convert string into a array 
            if (ch == target){
                return true;
            }
        }
        return false;
    }
}
