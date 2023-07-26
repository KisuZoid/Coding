<?php
//made by Kislay Anand
//Get username
$user=$_GET['u'];
?>
<html>
<head>
      <title>chatter</title>
	  <link rel='stylesheet' type='text/css' href='css/style.css'/>
	  <link href='http://fonts.googleapis.com/css?family=open+sans:400,300,600,700,800' rel='stylesheet' type='text/css'>
	  <script src="//code.jquery.com/jquery-1.11.0.min.js"></script>
	  <script src="javascript/chat.js"></script>
</head>
<body>
<!--made by Kislay Anand-->
<div class='chatContainer'>
    <div class='chatHeader'>
	     <h1>Welcome <?php echo ucwords($user); ?></h1>
	</div>	 
	<div class='chatMessages'>
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
	</div>
	<div class='chatBottom'>
	    <form action='#' onsubmit='return false;' id='chatForm'>
		      <input type='hidden' id='name' value='<?php echo $user; ?>'/>
			  <input type='text' name='text' value='' placeholder='type your message'/>
			  <input type='submit' name='submit' value='post' />
		</form>	  
	</div>
</div>
</body>
</html>	