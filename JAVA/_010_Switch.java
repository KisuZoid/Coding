import java.util.Scanner;

public class _010_Switch {
    public static void main(String[] args) {
        // switch :- Statement that allows a variable to be tested for equality against a list of value.

        System.out.print("Enter the name of a day: ");
        Scanner dayName = new Scanner(System.in);

        String day = dayName.nextLine().toLowerCase(); // toLowerCase() method will make the string in all lower case, so that whatever be the user input be a upper or lower case, it will coincide with out cases.

        switch (day) {
            case "monday":
                System.out.println("It is Monday!");
                break;

            case "tuesday":
                System.out.println("It is Tuesday!");
                break;
            
            case "wednesday":
                System.out.println("It is Wednesday!");
                break;

            case "thrusday":
                System.out.println("It is Thrusday!");
                break;

            case "friday":
                System.out.println("It is Friday!");
                break;

            case "saturday":
                System.out.println("It is Saturday!");
                break;

            case "sunday":
                System.out.println("It is Sunday!");
                break;

            default:
                System.out.println("Enter correct name of a day");
                break;
        }
        dayName.close();
    }
}

/* #Code Explain:-
 * : using switch(condition), condition will match to each case. 
 *      if the match will found at case "x" (i.e. condition = x), complete the task assigned to x, then breaks out of the loop.
 *          if we are not using break, then it will perform all cases after the matching case.
 *      else if the condition will not match with any case, then run the default statement and jumps out of the loop.
 * 
 * : break : The keyword is used to break out of the loop without proceeding further into the loop.
 */
