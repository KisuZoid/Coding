package Project; //Project is a file or package inside Java project file.
import javax.swing.JOptionPane;

public class _1_Gui {
    public static void main(String[] args) {
        String name = JOptionPane.showInputDialog("Enter your name");
        JOptionPane.showMessageDialog(null, "Hello, " + name);

        int age = Integer.parseInt(JOptionPane.showInputDialog("Enter your age"));
        JOptionPane.showMessageDialog(null, "You are " + age + " Years old");

        double height = Double.parseDouble(JOptionPane.showInputDialog("Enter your height"));
        JOptionPane.showMessageDialog(null, "You are " + height + " cm tall");
    }
}

/*
 * : for GUI(Graphical user inteface) -> notification plate
 *      import JOptionPane from swing which is in javax.
 * 
 *      showInputDialog() gives output in string,
 *          so, using it for age(int DataType), we have to convert in <int> DataType.
 *              we use "Integer.parseInt()" to convert form string to integer.
 *                      Parses the string argument as a signed decimal integer.
 *              similarly, Double.praseDouble() used to convert in <double> DataType.
 * 
 * : JOptionPane makes it easy to pop up a standard dialog box that prompts users for a value or informs them of something.
 *      Method Name	        Description
 *      showConfirmDialog	Asks a confirming question, like yes/no/cancel.
 *      showInputDialog	    Prompt for some input.
 *      showMessageDialog	Tell the user about something that has happened.
 *      showOptionDialog	The Grand Unification of the above three.
 * 
 * : void javax.swing.JOptionPane.showMessageDialog(Component parentComponent, Object message)
 *      parentComponent : determines the Frame in which the dialog is displayed; if null, or if the parentComponent has no Frame, a default Frame is used
 *      message : the Object to display
 * 
 */
