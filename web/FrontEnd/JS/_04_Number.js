var a, b;
a=31;
b=4;
console.log(a+b);   //addition -->35
console.log(a-b);   //subtraction -->27
console.log(a*b);   //multiplication -->124
console.log(a/b);   //division -->7.75
console.log(a%b);   //gives reminder when a/b -->3
console.log(a+=3);  //a = a+3 -->34
console.log(a-=3);  //a = a-3 -->31
console.log(a*=3);  //a = a*3 -->93
console.log(a/=3);  //a = a/3 -->31
console.log(a++);   //first assign the value of a, then increment it by 1. -->31
console.log(a); //-->32
console.log(++b);   //first increment the value of b by 1, then assign. -->5
console.log(b); //-->5

//similarly decrement variable: --a, a--

//Random
var n = Math.random(); //gives random numner between 0-1
console.log(n);

//manipulating the range
n*=6; //n = n*6
console.log(n);
//min=1, max=6
n = Math.floor(n) + 1; //Returns the greatest integer less than or equal to its numeric argument.
console.log(n);