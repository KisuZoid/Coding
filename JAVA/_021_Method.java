import java.util.Scanner;

public class _021_Method {
    public static void main(String[] args) {
        //Method = a block of code that is executed whenever it is called upon.

        //calling of method:
        System.out.println("method with argument:");
        greet_1("World"); //we are calling greet method from "static" method of "main()", that is why we have to use "static" keyword before this method.
        
        System.out.println();
        
        System.out.println("method without argument:");
        greet_2();
        
        System.out.println();
        
        System.out.println("Return type function with argument:");
        String func_1 = returnFunc_1("World"); //function returns Hello World that is assigned to variable func_1
        System.out.println(func_1); //print the value of the func_1

        System.out.println();

        System.out.println("Return type function with argument:");
        String func_2 = returnFunc_2();
        System.out.println(func_2);

        System.out.println();
        returnfunc_3();

        System.out.println();

        System.out.print("Add two number 3+4 = ");
        add(3,4);
    }

    //Declaring the our own method:
    static void greet_1(String name){
        System.out.println("Hello, " + name);
    }

    static void greet_2(){
        System.out.println("Hello, World");
    }

    static String returnFunc_1(String name){
        String greet = "Hello, " + name;
        return (greet);
    }

    static String returnFunc_2(){
        String greet = "Hello, World";
        return (greet);
    }

    static String returnfunc_3(){
        System.out.println("Another way: ");
        System.out.println("Hello, World");
        return ("Hurray"); // //i.e. if program will successfully run, it will return Hurray to the main function.
    }

    static int add(int x, int y){
        System.err.println(x + y);
        return 0; //i.e. if program will successfully run, it will return 0 to the main function.
    }
}

/* #Explain:
 * For creating own method or function:- Syntax
 * 
 *      <returnType> methodName(<arguments>){
 *           //Block of instruction for this method
 *      }
 * Convenvention for naming the method: first letter is small
 * 
 * Example:-
 * if method returns String of values to the main() method: <returnType> => String
 * if method returns integer values to the main() method: <returnType> => int
 * if method returns nothing to the main() method: <returnType> => void
 */
