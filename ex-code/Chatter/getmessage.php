<?php
    //getting these lousy messages
    $db=mysqli_connect("localhost","id8243976_chatter","kislay@anand");
    mysqli_select_db($db,"id8243976_chatter");
	//get messages
	$query=$db->prepare("SELECT * FROM messages");
	$query->execute();
	
	//fetch
	while($fetch=$query->fetch(PDO::FETCH_ASSOC))
	{
		$name=$fetch['name'];
		$message=$fetch['message'];
		
		echo"<li class='cm'><b>".ucwords($name)."</b>-".$message."</li>";
	}
?>