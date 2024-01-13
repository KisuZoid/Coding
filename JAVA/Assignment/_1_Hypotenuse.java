// Write a program form finding Hypotenue, where ask user to input Height and Base.
package Assignment;

import java.util.Scanner;

public class _1_Hypotenuse {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        double base, height, hypotenues;

        System.out.print("Enter Base of a Triangle: ");
        base = scanner.nextDouble();
        System.out.print("Enter Height of a Triangle: ");
        height = scanner.nextDouble();
        
        hypotenues = Math.sqrt(base*base + height*height);
        System.out.println("Hypotenues of a triangle of Height " + height + " and Base is " + base + " = " + hypotenues);
        scanner.close();
    }
}
