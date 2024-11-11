function isLeap(n){
    if ((n%4 === 0 && n%100 !== 0) || (n%400 === 0)){
        console.log("Year", n, "is Leap Year")
    }
    else{
        console.log("Year",n,"is not a Leap Year")
    }
}

isLeap(2004);
isLeap(2000);
isLeap(2003);
isLeap(2100);