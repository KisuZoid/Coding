public class _026_Class {
    //Setup constructor; (constructor have same name as class)
    String Name;
    int Age;
    double Weight;

    _026_Class(String name, int age, double weight){
        this.Name= name;
        this.Age= age;
        this.Weight= weight;
        //this keyword is replacable automatically. i.e. if we use human.Name means "this" will replace by "human".
        //      as per code example, name is assigned to human.Name
    }

    //Access object attribute within its class itself.
    void  eat(){
        System.out.println(this.Name + " is eating.");
    }

    void drink(){
        System.out.println(this.Name + " is drinking.");
    }
}
