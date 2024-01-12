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
 * 
 */