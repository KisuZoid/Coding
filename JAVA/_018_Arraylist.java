import java.util.ArrayList;

public class _018_Arraylist {
    public static void main(String[] args) {
        // ArrayList => a resizable array
        //              Elements can be added and removed after compilation phase 
        //              store reference data type

        //Syntax:
        ArrayList<String> food = new ArrayList<String>(); //food is the name of ArrayList that gonna store String.
        //ArrayList<String> food = new ArrayList<>(); // this is also correct

        food.add("pizza"); //adding value to the ArrayList
        food.add("hamburger");
        food.add("hotdog");
        System.out.println("Print ArrayList of String named as food: ");
        System.out.println(food + "\n");

        System.out.println("Number of values in ArrayList of String named as food: " + food.size());
        for(int i = 0; i < food.size(); i++){ //for finding the number of values in ArrayList, use size() method.
            System.out.println(food.get(i));  //for getting value at paticular index, use get() method and index is mentioned inside parentheses.
                                              // 0 indexed;
        }
        System.out.println(); //for new line

        //set or edit the value at particular index; use set(index wanna replace, replaced by)
        System.out.println("Before editing the value at 0th index: " + food.get(0));
        
        food.set(0, "bread");
        String getValue = food.get(0); 
        System.out.println("After editing the value at 0th index: " + getValue ); 
        System.out.println(); //for new line

        //remove element at index 2nd
        System.out.println("Before removing element at index 2nd: \n" + food.get(0) + " " + food.get(1) + " " + food.get(2) );
        food.remove(2);
        System.out.print("After removing: ");
        for(int i = 0; i < food.size(); i++){ 
            System.out.print(food.get(i) + " ");  
        }

        System.out.println("\n"); //for getting 2 new line i.e. same as pressing 2 times "Enter" in keyboard.

        //clear ArrayList : use clear() method to clear the element inside an ArrayList.
        food.clear();
        System.out.println("After clearing an ArrayList: ");
        for(int i = 0; i < food.size(); i++){ 
            System.out.print(food.get(i) + " ");  
        }
    }
}

/*
 * to store String in ArrayList: ArrayList<String>
 * to store particular DataType in ArrayList: ArrayList<DataType>
 * to store integer(int) in ArrayList : ArrayList<Integer> | use proper wrapper class corresponding to integer(Integer)
 */
