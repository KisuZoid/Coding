package Assignment;

import java.util.Scanner;

public class _3_TrianglePattern {
    public static void main(String[] args) {
                
        Scanner scanner = new Scanner(System.in);
        int length;
        String symbol = "";

        System.out.print("Enter # of edgeLenght: ");
        length = scanner.nextInt();
        System.out.print("Enter symbol to use: ");
        symbol = scanner.next(); 
        
        for(int i=1; i<=length; i++){
            for(int j=1; j<=i; j++){
                System.out.print(symbol);
            }
            System.out.println();
        }
        scanner.close();
    }
}