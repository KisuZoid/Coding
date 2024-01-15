public class _003_SwapVar{
    public static void main(String[] args){
        //Swapping of two variable:
        String x,y,temp; //declare variable in a single line.
        x = "Water";
        y = "Tube";
        temp = null; //"null" means no value.
//insted of declaring "temp=null", we can just declare temp as a string without assigning value, that will be same as "temp=null". 

        System.out.println("X:" + x + "\n" + "Y: " + y);

        System.out.println("\nNow after swapping: ");
        temp = y;
        y = x;
        x = temp;
        System.out.println("X:" + x + "\nY: " + y);
    }
}