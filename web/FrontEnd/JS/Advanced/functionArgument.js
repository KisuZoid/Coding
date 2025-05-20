//using chrome developer tool, write "debugger;" in the console to pause the execution of the code and inspect the values of variables at that point in time. This is useful for debugging purposes.

function add(num1, num2){
    return num1 + num2;
}

function subtract(num1, num2){
    return num1 - num2;
}

function multiply(num1, num2){
    return num1 * num2;
}

function divide(num1, num2){
    return num1 / num2;
}

//passing a function as an argument to another function
//--> this is called a higher order function
function calculator(num1, num2, operator){
    return operator(num1, num2);
}