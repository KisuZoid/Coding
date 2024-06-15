//string concatenation :: 
var firstName = "Kislay";
var lastName = "Anand";
console.log(firstName + " " + lastName); //--> Kislay Anand

console.log();

var firstID = "Kisu";
var lastID = "Zoid";
console.log(firstID + lastID) //--> KisuZoid

var ID = firstID + lastID;

//Find Length of string ::
console.log(ID.length); //--> ID.length provide length of the string ID(including spaces)


//Slicing ::
var word = "Kisu";
var sliced = word.slice(0, 1); // --> slicing out the particular character. slice(starting position, end position) || slicing will occur one character before end || Note : it is zero indexed
console.log(sliced); //--> display K

word = "01234";
console.log(word.slice(0,3)); //--> display 012

//Ques: 1.take input from user, 2. character count and remaining character out of 10, 3. display a message about the input count that is valid or invalid count.
const userInput = ""; //const is a keyword for constant --> means valid can not changed further
if (userInput !== null) // !== : not equals to, == : equals to, <= : less tha equals to, >= : greater than quals to
{
    if (userInput.length <= 10)
    {
        console.log("Valid count: your count is " + userInput.length + " And remaining " + (10 - userInput.length));
        console.log("Your input: " + userInput);
    }
    else{
        console.log("Invalid count: your count is " + userInput.length + " And remaining " + (10 - userInput.length));
        console.log("Your input: " + userInput.slice(0, 11)); //--> display only 10 characters
    }
}
else{
    console.log("you haven't wrote any sentences");
}