console.log("Hello World"); //print Hello world to the console/terminal

//typeof() --> function that gives us the datatype of value entered inside
//"+" will concatinate/add the value, concatinate strings and add up the numbers.

var x; //assigning that "x" is a variable
x = typeof("Hello"); //"x" is the variable/container that stores right hand side value.
console.log("x is " + x); //-->x is string

x = typeof("123");
console.log("x is " + x); //-->x is string

x = typeof(123);
console.log("x is " + x); //-->x is number

x = typeof(true);
console.log("x is " + x); //-->x is boolean

x = 3 + 4;
console.log("3 + 4 = " + x); //--> 3 + 4 = 7

x = "Kisu" + "Zoid";
console.log("I am " + x); //--> I am KisuZoid

x = "Kislay" + " " + "Anand";
console.log("My name is " + x); //--> My name is Kislay Anand

/* 
multi
Line
Comment
*/

//single line comment

//string of character or simply string are written in double or single quote. || symbol/character is written in single quote. || ";" use semi-colon at the end of statements

/*
    Data-Type   ::  Example
    1. String   ::  "Hello"
    2. Numbers  ::  123
    3. Boolean  :: true or false

    Note: in JS, data type is auto assigned.
        : "var" is the keyword for variable.

        ex: var MyName = "Kislay Anand";
*/