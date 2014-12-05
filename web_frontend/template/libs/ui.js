$(function() {
	$(".changeText").click (function () {
		$(".changedText").load(
			"./ajax.php",
			{
				action: "change", 
				text: $(".text").val()
			},
			function (data) {
				var ctr = false;
				$(window).keydown(function(event){
					shift = event.keyCode == 16;
					ctr = event.keyCode == 17;
				});
				$(document).keyup(function(event){
					if (event.keyCode == 16) shift = false;
					if (event.keyCode == 17) ctr = false;
				});
				$(".changed").mouseover (function () {
					//$(this).attr('ref');
					$(this).css({background: "#eee" });
					$(this).append(" = <span class='word'>"+$(this).attr('ref')+"</span>");
				});
				$(".changed").mouseout(function () {
					syn = $(this).attr('rel');
					$(this).text(syn);
					$(this).css({background: "none"});
				});
				$(".changed").click (function () {
					word = $(this).attr('ref');
					syn = $(this).attr('rel');
					if (shift) {
						$.get(
							"./ajax.php", 
							{
								action: "remove", 
								word: word, 
								syn: syn
							}
						);
						$(this).after(word);
						$(this).remove();
					} else if (ctr) {
						$(this).after(word);
						$(this).remove();
						return false;
					}
					var html = $.ajax({
						url: "./ajax.php",
						data: "action=select&word="+word,
						async: false
					}).responseText;
					$(this).after(html);
					$(this).next(".select").change(function (){
						$(this).after($(this).val());
						$(this).remove();
					});
					$(this).remove();
				});
			}
		);
	});
	$(".loading").ajaxStart(function(){
		$(this).show();
	});
	$(".loading").ajaxStop(function(){
		$(this).hide();
	});
});