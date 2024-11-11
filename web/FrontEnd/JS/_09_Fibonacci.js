//Every number is the sum of two previous ones(0 1 1 2 3 5 8 13 21...)
//using loop
/*
function fibonacci(n){
    var output = [];
    if (n===1){
        output = [0];
    }
    else if (n==2){
        output = [0, 1];
    }
    else{
        output = [0, 1];
        for (var i = 2; i < n; i++ ){
            output.push(output[output.length-1]+output[output.length-2]);
        }
    }
    console.log(output);
}

fibonacci(5);
*/

//using recurssion
function fibonacci(n){
    if (n===1){
        return 0;
    }
    else if (n===2){
        return 1;
    }
    else{
        for(var i=2; i<n; i++){
            n = fibonacci(n-1)+fibonacci(n-2);
            return n;
        }
    }
}

console.log(fibonacci(20));


