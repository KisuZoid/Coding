//add click event listener
$("h1").click(function() { //--> will add a click event listener to the h1 tag. When the h1 tag is clicked, it will change the color of the h1 tag to red.
    $("h1").css("color", "purple");
});

//without using jQuery
for (var i = 0; i < document.querySelectorAll("h1").length; i++) { //--> will select all the h1 tags and add a click event listener to each of them.
    document.querySelectorAll("h1")[i].addEventListener("click", function() { //--> will add a click event listener to the h1 tag. When the h1 tag is clicked, it will change the color of the h1 tag to red.
        document.querySelector("h1").style.color = "purple";
    });
}   


//add event listener to all the buttons
$("button").click(function() { //--> will add a click event listener to all the buttons. When any button is clicked, it will change the color of the h1 tag to purple.
    $("h1").css("color", "purple");
});


//keypress event listener
$("input").keypress(function(event){
    console.log(event.key); //--> will log the key that is pressed on the keyboard. It will log the key that is pressed on the keyboard.
    $("h1").text(event.key); //--> will change the text of the h1 tag to the key that is pressed on the keyboard.
});

//another way to add event listener
$("input").on("keypress", function(event){ //--> will add a keypress event listener to the input tag. When any key is pressed on the keyboard, it will change the text of the h1 tag to the key that is pressed on the keyboard.
    console.log(event.key); 
    $("h1").text(event.key); 
});

//hide, show, toggle
$("h1").hide(); //--> will hide the h1 tag. It will hide the h1 tag. The h1 tag will be hidden. 
$("h1").show(); //--> will show the h1 tag. It will show the h1 tag. The h1 tag will be shown.

// $("h1").toggle(); //--> will toggle the h1 tag. If the h1 tag is hidden, it will show it. If the h1 tag is shown, it will hide it.