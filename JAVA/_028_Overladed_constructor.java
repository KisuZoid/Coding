public class _028_Overladed_constructor {
    public static void main(String[] args) {
        // overloaded constructor => multiple constructors within a class with the same name,
        //                           but have different parameters
        //                           name + parameters = signature
        _028_Class pizza = new _028_Class("thick crust pizza", "tomato sauce", "mozzerella cheese", "pepperoni topping");
        _028_Class pizza1 = new _028_Class("Thick crust pizza1", "red chilli sauce", "1kg mozzerella cheese");

        System.out.println("Here are the ingredient of our pizza: with 4 parameters");
        System.out.println(pizza.bread);
        System.out.println(pizza.cheese);
        System.out.println(pizza.sauce);
        System.out.println(pizza.topping);
        System.out.println();

        System.out.println("Here are the ingreadient of our pizza: with 3 parameters");
        System.out.println(pizza1.bread);
        System.out.println(pizza1.sauce);
        System.out.println(pizza1.cheese);

    }
}
