public class _016_String {
    public static void main(String[] args) {
        // String => A reference data type that can store one or more characters.
        // reference data types have access to useful method.
        
        String nameString = "Kisu"; // declare String variable named as name 
        System.out.println("Main word: " + nameString + "\n");
        //Some useful method related to String data type:-

        //equals() method
        boolean equate_characters_in_string = nameString.equals("kisu"); //Check whether nameString variable(Kisu) is same as "kisu" or not, and returns Boolean value.
                                                       // Case sensative.
        System.out.println("\"Kisu\" is same as \"kisu\": " + equate_characters_in_string);

        //length() method
        int length_of_string = nameString.length(); // Return number of characters in variable nameString.
                                                    // Count spaces and special characters as well.
        System.out.println("Number of character in \"Kisu\": " + length_of_string);

        //charAt() method
        char character_at_prticular_index = nameString.charAt(0); //returns character at 0th index in value of nameString variable.
                                                                        // 0th indexed i.e. starts from 0th position
        System.out.println("Charater at 0th position in \"Kisu\": " + character_at_prticular_index);

        //indexOf() method
        int index_of_character = nameString.indexOf("K"); //return position of a particular character, returns integer.
        System.out.println("Position of \"K\" in \"Kisu\": " + index_of_character);

        //isEmpty() or isBlank() method
        boolean check_value_is_Empty = nameString.isEmpty(); // check nameString is empty or not and gives boolean value.
        System.out.println("Variable nameString(= \"Kisu\") is empty: " + check_value_is_Empty);

        String empty = "";
        System.out.println("Variable empty(= \"\") is Empty/Blank: " + empty.isEmpty());

        //toUppercase() and toLowercase() method
        String make_uppercase = nameString.toUpperCase(); //make string in all upper case
        String make_lowercase = nameString.toLowerCase(); //make string in all lower case

        System.out.println("Make \"Kisu\" in all Upper Case: " + make_uppercase);
        System.out.println("Make \"Kisu\" in all Lower Case: " + make_lowercase);

        //trim() method 
        String name = "   Kisu    ";
        System.out.println("Before trim method: " + name);
        String trim_whiteSpace = name.trim(); // trim or remove white spaces before and after the string
        System.out.println("After trim method: " + trim_whiteSpace);
        
        //replace() method
        String replace_character = nameString.replace('u', 's'); //replace the character with another.
                                                                                 // (oldChar, newChar) : character at first replaced with second.
        System.out.println("'u' in \"Kisu\" replaced with 's': " + replace_character);

    }
}
