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

    }
}
