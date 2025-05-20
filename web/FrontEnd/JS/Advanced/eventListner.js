//Event Listeners --> Layout
// target.addEventListner(type, listner[, options]);
//type: click, mouseover, keydown, keyup, etc. --> a case sensitive string representing the event type to listen for
//listner: a function to be called when the event occurs
//options: an object that specifies characteristics about the event listener
//options: capture, once, passive, signal

//click event listentner:
// document.querySelector("button").addEventListener("click", handleClick); //--> this will add a click event listener to the button element
//--> handleClick is used as a callback function instead of handleClick() because we don't want to call the function immediately(at the moment when website being open), we want to pass it as a reference to be called when the event occurs.

// function handleClick(){
//     alert("I got clicked button1!");
// }

//or by using an anonymous function:
// document.querySelectorAll("button")[1].addEventListener("click", function(){
//     alert("I got clicked button2!");
// });

// another way to add event listener to each button is to use a for loop:
const length = document.querySelectorAll(".drum").length; //--> this will get the number of buttons in the document
for (let i = 0; i < length; i++){ // --> let is used instead of var because let is block scoped and var is function scoped that means let is only accessible within the block it is defined in, while var is accessible within the function it is defined in.   
    //--> var gives the same value to all the buttons because it is function scoped and the loop will finish before the event listener is called, so all the buttons will have the same value of i which is length. ==> "I got clicked button 8!" for all buttons
    //--> let gives the correct value to each button because it is block scoped and the value of i will be different for each iteration of the loop.
    document.querySelectorAll(".drum")[i].addEventListener("click", function(){
        alert("I got clicked button" + (i+1) + "!");
    });
}
