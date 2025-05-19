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

//getter(get property):
// object.proterty;

//setter(set property):
// object.property = value;

//method -->method is something that object can do
// object.function();

//Getting the length:
document.getElementsByTagName("li").length; //--> gives the number of li elements in the document

//problem: change name of 3rd li
var changeNameThird = document.getElementsByTagName("li").item(2); //as there is 3 li element, and we have to select 3rd one. i.e use method item(index);
// document.getElementsByTagName("li") --> gives array of all the li elements, and we can select any element using index. i.e. 0,1,2,3... 
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

//herarcial selector:
// document.querySelector("#list a"); --> select all the "a" tag inside "list" id
// document.querySelector("li .item"); //--> select first element with this tag name, it gives only one element as id is unique in the document
// document.querySelectorAll("li .item"); //--> select all the elements with this tag name, it gives list of all the items

//select by class:
// document.getElementsByClassName("name_ofClass"); //--> select all the elements with this class name, it gives list of all the items
// document.getElementsByClassName("name_ofClass")[0]; //--> select first element with this class name
// document.querySelector(".name_ofClass"); //--> select first element with this class name

//select by id:
// document.getElementById("ID_ofElement"); //--> select element with this id name, it gives only one element as id is unique in the document
// document.querySelector("#ID_ofElement"); //--> select element with this id name, it gives only one element as id is unique in the document