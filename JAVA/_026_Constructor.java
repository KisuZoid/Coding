public class _026_Constructor {
    public static void main(String[] args) {
        // Constructor => Special method that is called when an object is instantiated(created).
        // Declare class _026_Class.java

        _026_Class human1 = new _026_Class("Kisu", 20, 67.70);
        _026_Class human2 = new _026_Class("Kislay", 20, 67);
        System.out.println("Name of 1st person: " + human1.Name);
        System.out.println("Name of 2nd person: " + human2.Name);

        human2.eat();
        human1.drink();
    }
}
