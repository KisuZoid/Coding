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

//callback function: it is a function that is passed as an argument to another function, and is executed after the other function has completed.
//for example, in the following code, the greet function is a callback function that is passed as an argument to the setTimeout function. The setTimeout function will execute the greet function after 2 seconds.
setTimeout(houseKeeper1.greet, 2000); // --> this will call the greet method of the object after 2 seconds

function greet(to) {
    console.log("Hello, " + to);
}
greet("John"); //--> output: Hello, John
greet("jane", "Doe"); //--> output: Hello, jane Doe
//this is a special keyword that refers to the current object

//callback function example:
function anotherEventListner(typesOfEvent, callback){
    //detect event code...

    var eventThatHappened = {
        eventType: "keypress",
        key: "p",
        durationOfKeyPress: 2
    }

    if (eventThatHappened.eventType === typesOfEvent) {
        callback(eventThatHappened);
    }
}

anotherEventListner("keypress", function(event) {
    console.log(event);
});
//--> output: {eventType: "keypress", key: "p", durationOfKeyPress: 2}
//--> this will call the callback function with the event object as an argument
// explaination: the anotherEventListner function is a function that takes two arguments, typesOfEvent and callback. The typesOfEvent is a string that represents the type of event that we want to listen for, and the callback is a function that will be called when the event occurs. The anotherEventListner function will detect the event and call the callback function with the event object as an argument. In this case, we are listening for a keypress event, and when the event occurs, we are calling the callback function with the event object as an argument. The output will be the event object that was passed to the callback function.
//--> this is a simple example of how to use callback functions in JavaScript. Callback functions are used to handle asynchronous events, such as user input, network requests, and timers. They allow us to write code that is more flexible and reusable, and they help us to avoid callback hell, which is a situation where we have too many nested callbacks that make the code difficult to read and maintain.

document.addEventListener("keypress", function(event){
    console.log(event);
});
//--> this will call the callback function with the event object as an argument when the key is pressed