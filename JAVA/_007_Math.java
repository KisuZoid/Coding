public class _007_Math {
    public static void main(String[] args) {
        double x = 3.14;
        double y = -10;

        //find maximum & minimum of two number
        double maxValue = Math.max(x, y);
        double minValue = Math.min(x,y);
        System.out.println("Maximum between " + x + " and " + y + " = " + maxValue);
        System.out.println("Minimum between " + x + " and " + y + " = " + minValue);
        
        //square root of a number
        double sqrtValue = Math.sqrt(x);
        System.out.println("Square root of " + x + " = " + sqrtValue);

        //Absolute value of a number i.e. modulus of a number (number without negative sign)
        double absValue = Math.abs(y);
        System.out.println("Absolute of " + y + " = " + absValue);

        //Rounding of a number
        double roundValue = Math.round(x);
        System.out.println("Rounding of " + x + " = " + roundValue);
        System.out.println("Rounding of " + 3.56 + " = " + Math.round(3.56));

        //Rounding up and down of a number
        double roundUp = Math.ceil(x);
        double roundDown = Math.floor(x);
        
        System.out.println("Rounding Up of " + x + " = " + roundUp);
        System.out.println("Rounding Down of " + x + " = " + roundDown);

        //printf() => is a method used to format output
        // %[flags][width][.precision][specifier-character] --> add %[one of those mentioned character] to format output --> % is the placeholder where the value will be printed.
        // %d --> integer, %f --> float, %s --> string, %c --> character, %b --> binary
        // %.2f --> 2 decimal places

        String name = "Rahul";
        char firstLetter = 'R';
        int age = 25;
        double height = 60.8;
        boolean isEmployed = true;
        System.out.printf("My name is %s, my first letter is %c, my age is %d, my height is %.2f and I am %b\n", name, firstLetter , age, height, isEmployed); //--> \n is for new line.
        //output: My name is Rahul, my first letter is R, my age is 25, my height is 60.80 and I am true
    }
}
