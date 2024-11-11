console.log(add(3, 5)); //add the value 3+5
console.log(add(2, 6)); //add the value 2+6
valuePrint(); //calling the valuePrint() function
converterGMtoKG(5000);
console.log(BMIcalc(67, 1.77));

Factorial_ForLoop(5);
Factorial_WhileLoop(5);
console.log(Factorial_Recurrsion(5) , "--> Recursion");

//making the function that will add the values
function add(a, b){//function with some arguments
    return a+b;
}

function valuePrint(){//function without arguments
    console.log("I am Kislay Anand");
}

function converterGMtoKG(a){
    console.log(a + "GM = " + a/1000 + "KG");//Here, the + operator is used to concatenate strings and variables. Everything is converted to a single string before being logged.
    console.log(a , "GM = " , a/1000 , "KG");//This uses commas to separate the values.Each value is logged separately, maintaining their types

}

function BMIcalc(weigth, heigth){
    return (Math.round(weigth/(Math.pow(heigth, 2))) + " is your BMI"); //Math.pow(value, power) --> helps to find power of the value
    //Math.round(value) --> it will round off the value
}

//Function calling it self --> Recurrsive function
function Factorial_Recurrsion(n){
    if (n===1 || n===0){ // "&& --> means And" "|| --> means Or"
        return 1;
    }
    return n*Factorial_Recurrsion(n-1);
}

//Loop:--> till the condition meet, follow the instruction.
//for loop: for(initial value, condition, operation){...}
function Factorial_ForLoop(n){
    num = 1;
    for(i = 1; i <= n; i++ ){
        num = i*num;
    }
    console.log(num, "-->For loop");
}

//while loop: while(condition){...}
function Factorial_WhileLoop(n){
    num = 1;
    i=1;
    while (i<=n){
        num = i*num;
        i++;
    }
    console.log(num, "-->While loop");
}