// Introduction using method:
package Assignment;

import java.util.Scanner;

public class _4_method {
    public static void main(String[] args) {
        Scanner intro = new Scanner(System.in);

        System.out.print("what is your Name: "); 
        String Name = intro.nextLine();
        System.out.print("What is your age: ");
        int Age = intro.nextInt();

        intro(Name, Age);
        intro.close();
    }
    
    static void intro(String name, int age){
        System.out.println("Hello, " + name + " You are " + age + " years old");
    }
}
