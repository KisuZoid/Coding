public class demo {//public this "demo class" is accessible everywhere
    public static void main(String[] args){
        /*
        main is a entry point 
        void in result type func. that gives result in final, as mentioned the result of void is void itself
        String[] args is string of arguments, arrays is stored in this variable
        public in 2nd line shows that this "main" function/method is public for program that can use further
        static func. is object independent that is this "main" function is not dependentent i.e. not an object of demo class
        */
        System.out.println(args[0]);
        //represent 1st argument from command line as args[0] is print | [0] means 1st array
    }
}
/*
javac demo.java
java demo 30
30 will print as it is 1st argument in command line

javac -d . demo.java i.e. it will make .class file in same directory
javac -d .. demo.java i.e. it will make .class file in previous directory
*/