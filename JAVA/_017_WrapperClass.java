public class _017_WrapperClass {
    public static void main(String[] args) {
        //Autoboxing:
        Boolean a = true; // Boolean wrapper class | use autoboxing to directly assign the primitive value to this reference data type;; similarly for others below:
        Character b = '@'; 
        //Integer c = 123;
        //Double d = 3.14;
        //String e = "Kisu";

        //Methods in Boolean wrapper class
        // a.<methodName>

        //Unboxing:
        if (a==true){
            System.out.println("This is true");
        }
        if (b=='@'){
            System.out.println("This is true");
        }
        
        //autoboxing : here we directly assign the value to the reference data type. i.e. we automatic converted the primitype values to its corresponding wrapper class 
        //unboxing : convert a wrapper class to its primitive value
    }
}

/*
* wrapper class => provides a way to use primitive data types as reference data types
*                  reference data type contains useful methods
*                                   can be used with collections (ex: ArrayList)
*                   Disadvantage: reference data type  are slower to acess  than primitive data type
*
*
* //Few Examples: Each primitive data type has corresponding wrapper class
* primitive    wrapper(convention: for wrapper class, first letter is capital)
* ----------  ---------
* boolean      Boolean
* char         Character
* int          Integer
* double       Double
*
*
* autoboxing => the automatic conversion that the java compiler makes between the primitive types and their corresponding object wrapper classes
* unboxing => the reverse of autoboxing, Automatic conversion of wrapper class to primitive.
*/
