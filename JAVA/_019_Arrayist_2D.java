import java.util.*;

public class _019_Arrayist_2D {
    public static void main(String[] args) {
        ArrayList<String> backeryList = new ArrayList<>();
        backeryList.add("pasta");
        backeryList.add("garlic bread");
        backeryList.add("donuts");

        ArrayList<String> productList = new ArrayList<>();
        productList.add("tomatoes");
        productList.add("zucchini");
        productList.add("pepper");

        ArrayList<String> drinksList = new ArrayList<>();
        drinksList.add("sode");
        drinksList.add("coffee");
        


        System.out.println("Our Backery List: " + backeryList);
        System.out.println("Our Product List: " + productList);
        System.out.println("Our Drinks List: " + drinksList);

        System.out.println();
        //element at particular index
        System.out.println("Print value at 0th index of our Backey List: " + backeryList.get(0));

        //2D ArrayList: combine the ArrayList of all the above. 
        // As the data type we want to store in comibined arraylist is ArrayList<String> becuase all above lists as arraylist of string.
        ArrayList<ArrayList<String>> groceryList = new ArrayList<>();
        groceryList.add(backeryList); // backeryList become 0th element for groceryList
        groceryList.add(productList);
        groceryList.add(drinksList);

        System.out.println("\nCombined List: \n" + groceryList);

        System.out.println("\nor\n"); //or
 
        for(int i = 0; i < groceryList.size(); i++){
            System.out.println(groceryList.get(i));
        } 
        
        System.out.println();

        System.out.println("0th element of comibined List(groceryList):\n" + groceryList.get(0));
        System.out.println("0th element inside 0th element of the groceryList: \n" + groceryList.get(0).get(0));
    }
}
