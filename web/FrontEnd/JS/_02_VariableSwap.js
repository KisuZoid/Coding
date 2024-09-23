var a, b;
a = 8;
b = 4;
console.log("Value of 'a' is " + a + " And Value of 'b' is " + b);

console.log(); //for empty line or new line, we can use this empty print or "\n"

var temp = a;
a = b;
b = temp;
console.log("Swapped Value of 'a' is " + a + " And swapped Value of 'b' is " + b + "\n"); //if we use double quote for a and b, then in results, first quote will end the main quote. --> i.e. generate error || so, for using that, we have to use space character i.e. \(back-slash)

//Swap without additional variable
var a, b;
a = 3;
b = 8;
console.log(a, " " , b + " \n ");

a = a+b;
b = a-b;
a = a-b;
console.log(a, " " , b + " \n ");


console.log("\"Kisu\" \n");
console.log('\t \'Kisu\''); // "\t" use to get tab.