import java.util.Scanner;

public class _9_If_else {
    public static void main(String[] args) {
        // if statement :- Perform a block of code if it's condition to be true.
        
        System.out.print("Enter your age? ");
        Scanner ageInput = new Scanner(System.in);

        int age =  ageInput.nextInt();

        if (age >= 18 && age <= 75){
            System.out.println("You are an adult!");
        }
        else if (age > 75){
            System.out.println("You are too old!");
        }
        else {
            System.out.println("Your are not an adult!");
        }

        ageInput.close();
    }
}
