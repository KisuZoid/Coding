import java.util.Scanner;

public class _011_While {
    public static void main(String[] args) {
        // While loop => It executes a block of code as long as the condition remains true.

        Scanner scanner = new Scanner(System.in);
        String name = "";

        while(name.isBlank()){
            System.out.print("Enter your name: ");
            name = scanner.nextLine();
        }

        System.out.println("Hello, " + name);
        scanner.close();
    }
}

/* #Another methode {Do...While Loop}
 * Syntax:
 *      do{
 *          (Statement);
 *      }
 *      while (condition);
 * : using do...while loop, we will always perform the block of code atleast once no matter the condition is true or false.
 *      if the condition will be true, then do the block of code once again and so on till the condition become false.
 * : #Code Explain:
 *      first perform the block of code  under do{} then repeat the block if the while condition be true.
 */

/* #Code Explain:-
 * : name is assigned to a blank character, i.e. "" (nothing inside double quote).
 * : while name is blank [name.isBlank()] i.e. condition become true, Execute the code within curly braces.
 *      print : Enter Your Name, and Input value assigned to the "name" variable.
 *              if user input the name, loop will exit because "name" variable is no more empty or blank i.e condition become false.
 * : Then execute the code below the while loop.
 */
