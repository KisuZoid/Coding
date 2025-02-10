//use html tree generator extention on chrome --> for visualising tree structure of HTML

document; //--> means call for html part of JS
//or both have same meaning
var document = Document; 


document.firstElementChild; //-->Returns the first child that is an element, and null otherwise. i.e <HTML> tag
document.firstElementChild.firstElementChild; //-->calling first child inside first child of document i.e. <Head> tag
document.firstElementChild.lastElementChild; //--> calling last child inside first child of document i.e. <body> tag

//call for particular tag
//select <H1> in our html
document.firstElementChild.lastElementChild.firstElementChild;

//manipulation of object
var heading = document.firstElementChild.lastElementChild.firstElementChild; //object H1 stored inside variable H1
heading.innerHTML = "New Head"; //change value
heading.style.color = "grey"; //change color

//select via name and apply method "click" on it
document.querySelector("input").click(); //--> by default our checkbox is checked

//getter(get property)
// object.proterty;

//setter(set property)
// object.property = value;

//method -->method is something that object can do
// object.function();


//problem: change name of 3rd li
var changeNameThird = document.getElementsByTagName("li").item(2); //as there is 3 li element, and we have to select 3rd one then use method item(index);
// document.getElementsByTagName("li") --> gives array
changeNameThird.innerHTML = "change";

//color of 1rd li using selector method --> select the element similar as CSS
document.querySelector("li a").style.color = "green"; //--> herarcial selector, child and parent provide space between two selector

document.querySelector("li.list"); //all is in same element, --> no space needed. --> this tag satisfies 3 elements but first one will gonna select by default, it will select all the class "list", which is in "li" tag.
//to select all:
document.querySelectorAll("li.list"); //--> selects all the element that matches, it gives list of all the items
//manipulate --> change 3rd li color
document.querySelectorAll("li.list")[2].style.color = "blue";


//change color of 2nd li
document.getElementsByTagName("li")[1].style.color = "purple"; //[index_ofElement]


//select by class
// document.getElementsByClassName("name_ofClass");

//select by id
// document.getElementById("ID_ofElement");


//add class "invisible" in html using javascript
document.querySelector("button").classList.add("invisible");

//we can perform all the task:
document.querySelector(".invisible").innerHTML = "button"; //change label of button from click to button.

//remove class "invisible" in html using JS:
// document.querySelector("button").classList.remove("invisible");

//toggle the query, i.e. if applied then remove, if not applied then add.
// document.querySelector("button").classList.toggle("invisible");