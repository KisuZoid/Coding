import java.util.ArrayList;

public class _020_ForEach_loop {
    public static void main(String[] args) {
        // for-each => traversing technique to iterate through the elements in an array/collection
        //              less steps, more readable
        //              less flexible

        //String[] animal = {"cat", "dog", "rat", "bird"};
    //or
        ArrayList<String> animal = new ArrayList<String>();

        animal.add("cat");
        animal.add("dog");
        animal.add("rat");
        animal.add("bird");

        System.out.println(animal + "\n");

        System.out.println("Name of animal in ArrayList: ");
        for(String i : animal){ //for i(index) which is String, in the collection named as animal.
            System.out.println(i);
        }
    }
}

// for(String i : animal){...} 
    /*
     * For each time in the loop, 
     * i(index) which represents String DataType, is assigned with a collection named as animal in same order as of collection.
     *      loop iterate itself till last element of collection, and each time index represent next element in collection. 
     */ 
