package OopPackage;

public class CarPackage {
    //Attributes(Characteristics)
    public String make = "Chevrolet";
    public String model = "Corvette";
    public int year= 2020;
    public String color = "blue";
    public double price = 50000.00;
        
    //Methods(What actions the car object perform)
    public void drive(){
        System.out.println("You drive the car");
    }
    public void brake(){
        System.out.println("You step on the breaks");
    }
}

/*
 * Methods and attributes are protected by default.
 *      to access the package method and attributes, we have to make it public by writing public keyword.
 */
