public class _015_Array_2D_1 {
    public static void main(String[] args) {
        //another method without allocation

        String[][] cars = {
                            {"Camaro", "Corvette", "Silverado"}, 
                            {"Mustand", "Ranger", "F-150"}, 
                            {"Ferrari", "Lambo", "Tesla"}
                        };
        
        for(int i = 0; i < cars.length; i++){
            System.out.println();
            for(int j = 0; j < cars[i].length; j++){ 
                System.out.print(cars[i][j] + " ");
            }
        }
    }
}
