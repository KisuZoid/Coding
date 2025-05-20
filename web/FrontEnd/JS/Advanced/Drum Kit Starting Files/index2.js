//same as index.js with some extra features

// var audio = new Audio("sounds/tom-1.mp3"); //--> this will create a new audio object and set the source to the tom-1 sound file
// function playSound(){
//     return audio.play();
// }
// document.querySelectorAll(".drum")[0].addEventListener("click", playSound); //--> this will play the audio when the button is clicked

// var audio2 = new Audio("sounds/tom-2.mp3");
// document.querySelectorAll(".drum")[1].addEventListener("click", function(){
//     audio2.play();
// });

// --> Add sound to the buttons when they are clicked
//--> we can use the Audio() constructor to create a new audio object and play it when the button is clicked
//--> we can use the play() method to play the audio
//--> we can use the pause() method to pause the audio
//--> we can use the currentTime property to set the current time of the audio
//--> we can use the duration property to get the duration of the audio
//--> we can use the volume property to set the volume of the audio
//--> we can use the loop property to set the loop of the audio





//using Array
var numberOfDrumButtons = document.querySelectorAll(".drum").length; //--> this will get the number of buttons in the document
for (var i = 0; i < numberOfDrumButtons; i++){
    document.querySelectorAll(".drum")[i].addEventListener("click", function(){
        this.style.color = "white"; //--> this will change the color of the button that was clicked

        var buttonInnerHTML = this.innerHTML;
        //Switch case statement to play sound
        switch (buttonInnerHTML) {
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
    })
}

// switch (expression){
//     case expression:

//         break;
//     default:
// }

// "this" refers to the button that was clicked basically its indicate the current button.
// console.log(this); --> this will give the inner HTML of the button that was clicked hence we can use innerHTML method.
// var buttonInnerHTML = this.innerHTML; //--> this will get the innerHTML of the button that was clicked
//--> this will get the innerHTML of the button that was clicked


//keyboard event
//--> we can use the keydown event to play sound when a key is pressed
document.addEventListener("keydown", function(event){
    //--> we can use the event.key property to get the key that was pressed
    //--> we can use the event.keyCode property to get the key code of the key that was pressed
    //--> we can use the event.which property to get the key code of the key that was pressed
    //--> we can use the event.code property to get the code of the key that was pressed

    var keyPressed = event.key; //--> this will get the key that was pressed
    switch (keyPressed) {
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
})
