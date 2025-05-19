//change the color of a tag using JS
// document.querySelector("a").style.color = "red"; //--> change the color of a tag to red

//change font size of a tag using JS
// document.querySelector("a").style.fontSize = "20px"; //--> change the font size of a tag to 20px

//change padding of a tag using JS
// document.querySelector("a").style.padding = "10px"; //--> change the padding of a tag to 10px 

//classList is used to add, remove, and toggle classes on an element
// document.querySelector("button").classList; //--> gives the list of all the classes of this element
// document.querySelector("button").classList[0]; //--> gives the first class of this element

 // <button class="btn">Click</button>
//add class "invisible" to the list of classes (classList) of button element in html document using javascript.
document.querySelector("button").classList.add("invisible");
// <button class="btn invisible">Click</button>  

//we can perform all the task:
document.querySelector(".invisible").innerHTML = "button"; //change label of button from click to button.

//remove class "invisible" in html using JS:
// document.querySelector("button").classList.remove("invisible");

//toggle the query, i.e. if applied then remove, if not applied then add.
// document.querySelector("button").classList.toggle("invisible");

//text manipulation:
// document.querySelector("button").innerHTML = "Click"; //--> change the text of button to "Click"
// document.querySelector("h1").textContent = "Hello"; //--> change the text of h1 to "Hello"
// document.querySelector("h1").innerText = "<strong>Hello</strong>"; //--> make the text of h1 bold 

//attribute manipulation:
// document.querySelector("a").getAttribute("href"); //--> get the value of href attribute of a tag
// document.querySelector("a").setAttribute("href", "https://www.google.com"); //--> set the value of href attribute of a tag to "https://www.google.com"
// document.querySelector("a").removeAttribute("href"); //--> remove the href attribute of a tag 