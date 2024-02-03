//Object Oriented Programming 
public class _024_Oop {
    public static void main(String[] args) {
        // Object => an instance of class that may contain attributes(characteristics of the object) and methods(actions)

        //class declated in another file: _024_Oop_ClassCar.java

        _024_Oop_ClassCar myCar = new _024_Oop_ClassCar();

        String carColor = myCar.color;
        System.out.println("Color of the car: " + carColor);
        System.out.println("Car Model: " + myCar.model);

        myCar.drive();
    }
}

/*
 * Declaration of class:
 *      <ClassName> UniqueName_forClass = new <ClassName_with_parentheses>;
 *      UniqueName is used for refering the class inside the code.
 *      Accessing the class functions:
 *          UniqueName_forclass.<function>
 */

