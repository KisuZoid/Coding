public class _015_Array_2D {
    public static void main(String[] args) {
        // 2D Array => an array of arrays
        // each element has a row and a column

        //representation of 2D array; "[][]"
        String[][] cars = new String[3][3]; //Array of 3*3 | [row][column]

        cars[0][0] = "Camaro "; //row 0, column 0
        cars[0][1] = "Corvette "; //row 0, column 1
        cars[0][2] = "Silverado"; //row 0, column 2

        cars[1][0] = "Mustand "; //row 1, column 0
        cars[1][1] = "Ranger "; //row 1, column 1
        cars[1][2] = "F-150"; //row 1, column 2

        cars[2][0] = "Ferrari "; //row 2, column 0
        cars[2][1] = "Lambo "; //row 2, column 1
        cars[2][2] = "Tesla"; //row 2, column 2

        for(int i = 0; i < cars.length; i++){
            System.out.println();
            for(int j = 0; j < cars[i].length; j++){ //cars[i].lenght means lenght of our "i"th row that we are currently on.
                System.out.print(cars[i][j]);
            }
        }
    }
}
