import java.util.Scanner;

public class _009_If_else {
    public static void main(String[] args) {
        // if statement :- Perform a block of code if it's condition to be true.
        
        System.out.print("Enter your age? ");
        Scanner ageInput = new Scanner(System.in);

        int age =  ageInput.nextInt();

        if (age > 0){
            if (age >= 18 && age <= 75){
                System.out.println("You are an adult!");
            }
            else if (age > 75){
                System.out.println("You are too old!");
            }
            else if (age >=13 && age < 18) {
                System.out.println("Your are a teenager!");
            }
            else {
                System.out.println("You are a kid!");
            }    
        }
        else if (age == 0){
            System.out.println("New born baby!");
        }
        else {
            System.out.println("Your age is invalid!!");
        }
        
        ageInput.close();
    }
}
