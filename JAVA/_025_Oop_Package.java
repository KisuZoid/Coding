//making of our own Package "OopPackage" inside which CarPackage is a part. 
import OopPackage.CarPackage; //importing the package

public class _025_Oop_Package {
    public static void main(String[] args) {
        CarPackage car = new CarPackage();
        System.out.println("Color of the car: " + car.color);
        car.drive();
    }
}