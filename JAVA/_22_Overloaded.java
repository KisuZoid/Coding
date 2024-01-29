public class _22_Overloaded {
    public static void main(String[] args) {
        // overloaded methods => method that share the same name but have different parameters
        //                        method name + parameters = method signature
        int x;
        double y;
        x = add(1, 2);
        System.out.println(x);

        x = add(1, 2, 3);
        System.out.println(x);

        y = add(1.0, 2.2);
        System.out.println(y);

         
    }
    //each method have unique method signature
    
    static int add(int a, int b){
        System.out.println("overloaded Method #1");
        return a+b;
    }
    static int add(int a, int b, int c){
        System.out.println("overloaded Method #2");
        return a+b+c;
    }
    static double add(double a, double b){
        System.out.println("overloaded Method #3");
        return a+b;
    }
}
