public class Var_2{
    public static void main(String[] args){
        int x; //declaration of variable
        x = 123; //assign the value to the variable.
        /*
        * we can use this as well:
        *  int x = 123; //initialization
        */
        System.out.print("Integer: ");
        System.out.println(x);

    //using string concatination
        long y = 12345678901234567L;
        System.out.println("Long: " + y);

        float float_var = 3.14567f;
        System.out.println("Float: " + float_var);

        char symbol = '@';
        System.out.println("Char: " + symbol);

        boolean z = true;
        System.out.println("boolean True: " + z);

        String string = "Kisu";
        System.out.println("String: " + string);
    }
}

/*
 * #Code Explain:-
 * : Variable is a placeholder for a value that behaves as the value it contains.
 * : <data_type> x = 123; here x behaves like integral container.
 * : <data_type> y = "String"; here, y behaves like string. and everthing inside double quote is a string.
 * : <data_type> -> is a declaration for a variable, that specify what type of value, the variable gonna contain.
 * <basic dataType> -> <Value>
 *      boolean -> ture(1) or false(0)
 *      byte    -> -128 to -127
 *      short   -> -32,720 to 32,767
 *      int     -> -2 billion to 2 billion
 *      long    -> -9 quintillion to 9 quintillion
 *                      -> we have to use "L" at the end of number.
 *      float   -> fractional number upto 6-7 digits
 *          ex: 3.141592f -> for assigning value to the float, we have to use "f" at the end of number.
 *      double  -> fractional number upto 15 digits
 *          ex: 3.141592653589793
 *      char    -> single character/letter/ASCII value written in single quote 
 *          ex: 'c'  
 * (☝️upper 8 data types are primitive data type, rest all are user defined reference data type)
 * 
 * (Anything with a reference data type begins with capital letter)
 *      String  -> a sequence of characters written in double quote.
 *          ex: "string"
 */