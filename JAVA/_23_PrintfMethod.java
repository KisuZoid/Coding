public class _23_PrintfMethod {
    public static void main(String[] args) {
        /*
         * printf() => an optional method to cotrol, format, and display text to the console window.
         *              contains two arguments: format string + (object/variable/value)
         *              % [flags] [precision] [width] [conversion-character]
         */
        
         //Specifier specifies where(place/position) to print the value.
         System.out.printf("This is format string and the value is #1:  %d\n",123);
         System.out.printf("The value is #2: %d and This is format string\n\n",123);

         boolean myBool = true;
         char myChar = '@';
         String myString = "Kisu";
         int myInt = 2;
         double myDouble = 100;

         System.out.printf("%b\n", myBool);
         System.out.printf("%c\n", myChar);
         System.out.printf("%s\n", myString);
         System.out.printf("%d\n", myInt);
         System.out.printf("%f\n", myDouble);

         //[flag]
         System.out.println("Flag: \n");
         double num = 100001;
         double minusValue = -1000001;
         System.out.printf("%f \n", num);
         System.out.printf("%+f \n", num);
         //represent with minus sign:
         System.out.printf("%f \n", minusValue);
         System.out.printf("%20f \n", num);
         System.out.printf("%-20f \n", num);
         System.out.printf("%020f \n", num);
         System.out.printf("%,f \n", num);
    }
}

/* #format specifier:  Represents:
 *      %d           => decimal/integer
 *      %f           => float/double
 *      %s           => string
 *      %b           => boolean
 *      %c           => char                 
 */

/*[width] ("." represents white spaces)
 * minimum number of characters to be written as output:
 * System.out.printf("Hello %s", myString);
 * //output: Hello Kisu
 * System.out.printf("Hello %10s", myString);
 * //output: Hello ......Kisu 
 * //introduce extra spaces before display the string. extra space is same as subtract number mentioned and number of character in string.
 * System.out.printf("Hello %-10s", myString); //reverse order or spacing after string
 * //output: Hello Kisu......
 * applicable when number mentioned is greater that number of character
 */

/*[precision]
 * sets number of digits when outputting floating point values
 * System.out.printf("%f", myDouble);
 * //output: 100.000000
 * System.out.printf("%.2f", myDouble);
 * //output: 100.00
 */

/*[flags]
 * adds an effect to output based on flag added to format specifier
 * - : left-justify
 * + : output a plus(+) or minue(-) sign for a numeric value
 * 0 : numeric values are zero-padding
 * , : comma grouping separator if number > 1000
 */

