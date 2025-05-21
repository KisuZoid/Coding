//detecting the button that was clicked
var numberOfDrumButtons = document.querySelectorAll(".drum").length;
for (var i = 0; i < numberOfDrumButtons; i++){
    document.querySelectorAll(".drum")[i].addEventListener("click", function(){
        this.style.color = "white"; //--> this will change the color of the button that was clicked

        var buttonInnerHTML = this.innerHTML; //innerHTML example: <button class="drum">w</button> --> here w is the innerHTML
        makeSound(buttonInnerHTML); //--> this will get the innerHTML of the button that was clicked and pass it to the function
        buttonAnimation(buttonInnerHTML);
    });
}

//detecting the keyboard press
document.addEventListener("keydown", function(event){ // here event is the parameter that will be passed to the function, event is an object that contains information about the event that occurred. In this case, it will contain information about the key that was pressed
    makeSound(event.key); //--> event.key : this will get the key that was pressed and pass it to the function
    buttonAnimation(event.key);
});

//  meaning and difference between function() and function(event) is that function() is a function that does not take any parameters, while function(event) is a function that takes an event object as a parameter. The event object contains information about the event that occurred, such as the key that was pressed, the mouse button that was clicked, etc. In this case, we are using function(event) to get the key that was pressed and pass it to the makeSound function. in other words, function(event) is a more specific version of function() that allows us to access information about the event that occurred.

function makeSound(key){ //key is the parameter that will be passed to the function
    //--> this will get the key that was pressed
    switch (key) {
        case "w":
            var tom1 = new Audio("sounds/tom-1.mp3");
            tom1.play();
            break;
        case "a":
            var tom2 = new Audio("sounds/tom-2.mp3");
            tom2.play();
            break;
        case "s":
            var tom3 = new Audio("sounds/tom-3.mp3");
            tom3.play();
            break;
        case "d":
            var tom4 = new Audio("sounds/tom-4.mp3");
            tom4.play();
            break;
        case "j":
            var snare = new Audio("sounds/snare.mp3");
            snare.play();
            break;
        case "k":
            var crash = new Audio("sounds/crash.mp3");
            crash.play();
            break;
        case "l":
            var kickBass = new Audio("sounds/kick-bass.mp3");
            kickBass.play();
            break;
        default:
            alert("Invalid Key Pressed");
    }  
}  


// document.addEventListener("keydown", function(event){
//     console.log(event);
// });
//--> this will get the key that was pressed

//Animation 
function buttonAnimation(currentKey){
    var activeButton = document.querySelector("." + currentKey)// here, we are selecting the element with the class name that matches the key that was pressed. as ".w" is for class, hence we are using "."
    activeButton.classList.add("pressed");
    //add delay
    setTimeout(function(){
        activeButton.classList.remove("pressed");
    }, 100)
}