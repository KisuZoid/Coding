//Ojects in JS
//Objects are a collection of key-value pairs

//houseKeeper1 is an object, with properties and methods
//Properties are the values of the object for example, yearsOfExperience, name, hasWorkPermit, age, cleaningRepertoire
//Methods are the functions of the object, for example, greet
var houseKeeper1 = {
    yearsOfExperience: 10,
    name: "John",
    hasWorkPermit: true,
    age: 30,
    cleaningRepertoire: ["bathroom", "kitchen", "living room"],
    greet: function() {
        console.log("Hello, my name is " + this.name);
    }
}

// Constructor function: it is a function that creates an object
// class is a blueprint for creating objects
class HouseKeeper { // --> class name should be capitalized
    // constructor is a special method for creating and initializing an object created with a class
    constructor(yearsOfExperience, name, hasWorkPermit, age, cleaningRepertoire) {
        this.yearsOfExperience = yearsOfExperience;
        this.name = name;
        this.hasWorkPermit = hasWorkPermit;
        this.age = age;
        this.cleaningRepertoire = cleaningRepertoire;
        this.greet = function () {
            console.log("Hello, my name is " + this.name);
        };
    }
}

// both are same but the class is a more modern way of creating objects

// function HouseKeeper(yearsOfExperience, name, hasWorkPermit, age, cleaningRepertoire) {
//     this.yearsOfExperience = yearsOfExperience;
//     this.name = name;
//     this.hasWorkPermit = hasWorkPermit;
//     this.age = age;
//     this.cleaningRepertoire = cleaningRepertoire;
//     this.greet = function () {
//         console.log("Hello, my name is " + this.name);
//     };
// }

//initializing the object using the constructor function
var houseKeeper1 = new HouseKeeper(10, "John", true, 30, ["bathroom", "kitchen", "living room"]); // --> this will create a new object using the constructor function, new keyword is used to create a new object.
var houseKeeper2 = new HouseKeeper(5, "Jane", true, 25, ["bathroom", "kitchen"]);

//calling the method of the object
houseKeeper1.greet(); // --> this will call the greet method of the object
houseKeeper2.greet(); 

//calling the properties of the object
console.log(houseKeeper1.yearsOfExperience); // --> this will call the yearsOfExperience property of the object
console.log(houseKeeper2.name); // --> this will call the name property of the object
console.log(houseKeeper2.hasWorkPermit); // --> this will call the hasWorkPermit property of the object