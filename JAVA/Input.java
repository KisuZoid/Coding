import java.util.Scanner;

public class Input{
    public static void main(String[] args){
        Scanner scanner = new Scanner(System.in); //a new Scanner that produces values scanned from the specified input stream.

        System.out.println("What is your name? ");
        String name = scanner.nextLine();

        System.out.println("Hello, " + name);

    }
}

/*
 * #Code Explain:-
 * : Scanner class is found in java utility package of the java library. 
 *      to use Scanner, we have to import that package "java.util.Scanner"
 *      "import java.util.Scanner" means import Scanner from utility package which is inside java library.
 * :  
 * 
 */