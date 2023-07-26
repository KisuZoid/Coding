$(function() {
	$(document).on('submit','#chatForm',function(){
		var text=$.trim($("#text").val());
		var name=$.trim($("#name").val());
		
		if(text !="" && name !=""){
			$.post('chatposter.php',{text:text,name:name},function(data){
				$(".chatMessages").append(data);
			});
		}else{
			alert("data missing");
		}
	});
	function getMessages(){
		$.get('getmessage.php',function(data){
			$(".chatMessages").html(data);
		});
	}
	
	setInterval(function(){
		getMessages();
	},500);
});