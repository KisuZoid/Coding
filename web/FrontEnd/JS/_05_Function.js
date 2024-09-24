console.log(add(3, 5)); //add the value 3+5
console.log(add(2, 6)); //add the value 2+6
valuePrint(); //calling the valuePrint() function
converterGMtoKG(5000);


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
