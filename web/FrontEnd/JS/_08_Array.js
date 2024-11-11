//Array: collection of similar kind of datatype & it is zero indexed
var egg = [0, 11, 22, 33, 44, 55, 66] //initializing the array
console.log(egg[0]);
console.log(egg[3]);

var len = egg.length; //gives total length of an array, (7)
console.log(len);

var search = egg.includes(11); //it will search that value "11" is in array or not and return the boolean value(0(false) or 1(true))
console.log(search);

//push or pop : Push will add item to the end and pop will remove from the end
egg.push(77);
console.log(egg);

var n = egg.pop();
console.log(egg);
console.log(n); //display popped item
