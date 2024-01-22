public class _014_Array_1 {
    public static void main(String[] args) {
        //Another way to create an array;
        /*
         * By first allocating the amount of array
         * then storing the values later on in the program.
         */

        String[] car = new String[3]; // 3 values are there in the array of string "car".

        car[0] = "BMW";
        car[1] = "Tesla";
        car[2] = "Ferrari";

        //for loop to display the element of an array;
        System.out.print("Array of string \"car\": "); 
        for(int i=0; i< car.length; i++){ //car.length will give the number of values in an array of string  "car".
            System.out.print(car[i] + " ");
        }
    }
}
