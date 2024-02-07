import java.util.Random;

public class _027_Class {
    //declare global variable
    int number = 0;
    Random random;

    _027_Class(){
        random = new Random();
        roll();
    }

    void roll(){
        number = random.nextInt(6)+1;
        System.out.println(number);
    }
//-or-
    /*//Declared locally
     * _027_Class(){
     *   Random random = new Random();
     *   int number = 0;
     *   roll(random, number);
     *   }
     *
     *   void roll(Random random, int number){
     *       number = random.nextInt(6)+1;
     *       System.out.println(number);
     *   }
     */
}
