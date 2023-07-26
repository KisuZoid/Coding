<?php
    //the legendary chat poster
	
	$db=mysqli_connect("localhost","id8243976_chatter","kislay@anand");
	if(!$db)
	{
		die('could not connect...' .mysqli_error());
	}
	mysqli_select_db($db,"id8243976_chatter");
	//secure the chat
	if(isset($_POST['text']) && isset($_POST['name']))
	{
		$text=strip_tags(stripslashes($_POST['text']));
		$name=strip_tags(stripslashes($_POST['name']));
		
		if(!empty($text) && !empty($name))
		{
			$insert=$db->prepare("INERT INTO messages VALUES('','".$name."','".$text."')");
			$insert->execute();
			
			echo"<li class='cm'><b>" .ucwords($name)."</b> - ".$text."</li>";
		}
	}
?>	
