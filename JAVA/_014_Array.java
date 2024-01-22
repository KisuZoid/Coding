public class _014_Array {
    public static void main(String[] args) {
        // Array => Used to store multiple values of same type in a single variable.

        String[] car = {"BMW", "Tesla", "Ferrari"}; //Syntax to declare string car as an array.
        System.out.println("Location of array \"car\" in memory " + car + "\n");
        System.out.println("Array of string \"car\": " + car[0] + " " + car[1] + " " +car[2] + "\n");
        System.out.println("Before re-assigning: car[0] = " + car[0]);
        
        
        //Re-Assigning/Changing the value for car[0] i.e. 1st element of an array. 
        car[0] = "Mustand";
        System.out.println("After re-assigning: car[0] = " + car[0] + "\n");
        System.out.println("Array of string \"car\" after re-assigning: " + car[0] + " " + car[1] + " " +car[2]);

    }
}

/* #Code Explain:
 * Array is zero indexed i.e. 1st element is at 0th position, 2nd at 1st and so on.
 * To represent an array : use "[]".
 */
