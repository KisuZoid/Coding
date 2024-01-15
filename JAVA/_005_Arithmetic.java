public class _005_Arithmetic {
    public static void main(String[] args) {
        // expression = operands & operators
        // operands = values, variables, numbers, quantity
        // arithmatic operator = + - * / % A++ ++A A-- --A

        System.out.println(3 + 4); // Direct use without declaration

        int num_1, num_2, add, sub; // Declare then Assigning the value
        num_1 = 3;
        num_2 = 4;
        add = num_1 + num_2;
        sub = num_2 - num_1;
        System.out.println(num_1 + "+" + num_2 + " = " + add); //Addition
        System.out.println(num_2 + "-" + num_1 + " = " + sub); //Subtraction

        int post;

        post = 5;
        System.out.println("\nBefore increment(x) = " + post);
        System.out.println("At increment(x++) = " + post++);
        System.out.println("After post increment(x) = " + post);

        post = 5;
        System.out.println("\nBefore decrement(x) = " + post);
        System.out.println("At decrement(x--) = " + post--);
        System.out.println("After post decrement(x) = " + post);

        int pre;

        pre = 5;
        System.out.println("\nBefore increment(x) = " + pre);
        System.out.println("At increment(++x) = " + ++pre);
        System.out.println("After pre increment(x) = " + pre);

        pre = 5;
        System.out.println("\nBefore decrement(x) = " + pre);
        System.out.println("At decrement(--x) = " + --pre);
        System.out.println("After post decrement(x) = " + pre + "\n");

        int num_3 = 2;
        System.out.println(4 + "/" + num_3 + " = " + 4/num_3); //Division
        System.out.println(num_2 + "%" + num_1 + " = " + num_2%num_1); //Modulo, A%B : Gives reminder when we divide A to B.
        System.out.println(num_1 + "*" + num_2 + " = " + num_1*num_2); //Multiplication
    }
}

/* #Code Explain:- (atithmetic operator)
 * + : Addition
 * - : subtraction
 * * : multiplication
 * / : division
 * % : returns the division reminder
 * ++A => increase value of A by 1, then assign it to A. i.e. ++8 = 9.
 * A++ => define A then increase value of A by 1. i.e. 8++ = 8 and new value will become 9 for next time.
 * --A => decrease value of A by 1, then assign it to A. i.e. --8 = 7.
 * A-- => define A then decrease value of A by 1. i.e. 8-- = 8 and new value will become 7 for next time.
 */
