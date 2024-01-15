import java.util.Random;

public class _008_Random {
    public static void main(String[] args) {
        Random random = new Random();

        int x = random.nextInt(6); //Bound the randomness in selection of values between 0 to 5 total 6 values. (it is 0 indexed. so, value starts with 0) 
        double y = random.nextDouble(6) + 1; //Bound the randomness in selection of values between 0 + 1 to 5 + 1 total 6 values. (it is 0 indexed. so, value starts with 0 + 1 = 1) 
        boolean z = random.nextBoolean();
        System.out.println("Random for int between 0-5: " +x);
        System.out.println("Random for double between 0-5 + 1 => 1-6: " +y);
        System.out.println("Random for boolean value: "+z);
    }
}
