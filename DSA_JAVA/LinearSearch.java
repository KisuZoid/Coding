//Ques: array = [18, 12, 9, 14, 77, 50], find 14 exist in array or not.
public class LinearSearch {
    public static void main(String[] args){
        int arr[]= {18, 12, 9, 14, 77, 50};
        int num = 14;
        int ans = Search(arr, num);
        System.out.println(ans);


    }
    
    //Professional Way Method 0:
    static int Search(int arr[], int target){
        if (arr.length==0){
            return -1;
        }
        
        //using for loop
        for (int i = 0; i < arr.length-1; i++){
            int element = arr[i];
            if (element == target){
                return element;
            }
        }
        return -1;
    }
}

//Method 1:
/*
int arr[] = {18, 12, 9, 14, 77, 50}; //length = 6
//Length
System.out.println(arr.length); 

//using for loop
for (int i = 0; i < arr.length-1; i++ ){ //max value of i is 5 as array is 0th indexed
    if(arr[i] == 14){
        System.out.println("Yes, 14 Exists");
        break;
    }
    else{
        continue;
    }
}
 */
