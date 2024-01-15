import java.util.Scanner;

public class _13_NestedLoop {
    public static void main(String[] args) {
        // nested loops : a loop isnide a loop
        
        Scanner scanner = new Scanner(System.in);
        int rows;
        int columns;
        String symbol = "";

        System.out.print("Enter # of rows: ");
        rows = scanner.nextInt();
        System.out.print("Enter # of columns: ");
        columns = scanner.nextInt();
        System.out.print("Enter symbol to use: ");
        symbol = scanner.next(); //next() method is used when we read a single character(char).

        for(int i=1; i<=rows; i++){
            for(int j=1; j<=columns; j++){
                System.out.print(symbol);
            }
            System.out.println();
        }
        scanner.close();
    }
}

/* #Code Explain:
 * : Functionality is same as for loop, but difference is :
 *      execute one condition inside 1st "for" loop, and run through all the condition of insider loop.
 *          repeat the process till the condition is true for 1st loop.
 */
