public class LinearSearch {
    //Ques: array = [18, 12, 9, 14, 77, 50], find 14 exist in array or not.
    public static void main(String[] args){
        int arr[] = {18, 12, 9, 14, 77, 50}; //length = 6
        //Length
        System.out.println(arr.length); 

        //using for loop
        for (int i = 0; i < arr.length-1; i++ ){
            if(arr[i] == 14){
                System.out.println("Yes, 14 Exists");
                break;
            }
            else{
                continue;
            }
        }
    }
}
