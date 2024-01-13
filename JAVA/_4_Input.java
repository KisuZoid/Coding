import java.util.Scanner;
//more will be covered under oops.
public class _4_Input{
    public static void main(String[] args){
        Scanner scanner = new Scanner(System.in); //Construct a new Scanner that produces values scanned from the specified input stream.

        System.out.println("What is your name? ");
        String name = scanner.nextLine(); // Here, we are using nextLine() method to read the line of text.

        System.out.println("What is your age? ");
        int age = scanner.nextInt();
        scanner.nextLine();

        System.out.println("What is your favourite food? ");
        String food = scanner.nextLine();

        System.out.println("Hello, " + name);
        System.out.println("Your age is " + age);
        System.out.println("You like " + food);

        scanner.close(); //for closing the scanner
    }
}

/*
 * #Code Explain:-
 * : Scanner class is found in java utility package of the java library. 
 *      to use Scanner, we have to import that package "java.util.Scanner"
 *      "import java.util.Scanner" means import Scanner from utility package which is inside java library.
 * : "scanner" is the name for class Scanner.
 * : nextLine() method, this method will read the whole line.
 *      when we press enter i.e. \n escape character will introduce.
 *          this method will read to escape method.
 * : nextInt() will return the int part of the text. 
 *      i.e. escape character will remain in Scanner.
 *      so, when we use nextLine() just after nextInt(), it will hit escape character and stop the line.
 *          to prevent this to happen, we have to use nextLine() twice. 
 * 
 * : System : The System class contains several useful class fields and methods.
 *               Among the facilities provided by the System class are standard input, standard output, and error output streams
 * 
 *          System.in : "in" stands for Standard Input Stream. 
 */