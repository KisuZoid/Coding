// 1. jQuery is a JavaScript library
// $()
// or 
// jQuery()

// 2. jQuery is a cross-browser JavaScript library designed to simplify the client-side scripting of HTML. 

//Color using JQuery
$("h1").css("color", "red"); 
//--> change the color of the h1 tag to red. Selects the h1 tag and applies the CSS color property to it. 

//Other Method: "when the document is ready then it will change the color of the h1 tag to red" --> use when jquery method(url) is linked within Head tag.
$(document).ready(function() {
    $("h1").css("color", "red");
});

// "Note: use minify of javascript and css for faster loading of the page. Minify is a process of removing all unnecessary characters from source code without changing its functionality. It is used to reduce the size of the file and improve load time.";

//select all of the buttons
$("button").css("background-color", "skyblue"); //--> will select all the buttons and change the background color to skyblue.

//adding and removing classes
$("h1").addClass("big-title"); //--> will add the class big-title to the h1 tag.
$("h1").removeClass("big-title"); //--> will remove the class big-title from the h1 tag.

//adding many classes
$("h1").addClass("big-title margin-50"); //--> will add the classes big-title and margin-50 to the h1 tag.
$("h1").toggleClass("big-title margin-50"); //--> will toggle the class big-title on the h1 tag. If the class is present, it will remove it. If the class is not present, it will add it.

//changing the text of the h1 tag
$("h1").text("New World"); //--> will change the text of the h1 tag to New World.

//checking the element have the class or not
$("h1").hasClass("big-title"); //--> will check if the h1 tag has the class big-title or not. It will return true or false.

//adding tag into the h1 tag
$("h1").html("<em>New World</em>"); //--> will add the tag <em> into the h1 tag. It will change the text of the h1 tag to New World and make it italic.

// manipulate attribute
$("#url").attr("href", "https://www.google.com"); //--> will change the href attribute of the a tag to https://www.google.com. It will change the link of the a tag to google.com.


//add element before or after the h1 tag
$("h1").before("<button>New</button>"); //--> will add a button tag before the h1 tag. It will add a button tag before the h1 tag. The button tag will be added before the h1 tag.

$("h1").after("<button>New</button>"); //--> will add a button tag after the h1 tag. It will add a button tag after the h1 tag. The button tag will be added after the h1 tag.
$("h1").prepend("<button>New</button>"); //--> will add a button tag inside the h1 tag. It will add a button tag inside the h1 tag. The button tag will be added inside the h1 tag.

$("h1").append("<button>New</button>"); //--> will add a button tag inside the h1 tag. It will add a button tag inside the h1 tag. The button tag will be added inside the h1 tag.

//remove 
$("button").remove(); //--> will remove the button tag from the h1 tag. It will remove the button tag from the h1 tag. The button tag will be removed from the h1 tag.

