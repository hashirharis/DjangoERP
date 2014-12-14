/**
 * Unicorn Admin Template
 * Version 2.0
 * Diablo9983 -> diablo9983@gmail.com
**/

$(document).ready(function(){
	
	var msg_template = '<p><span class="msg-block"><strong></strong><span class="time"></span><span class="msg"></span></span></p>';
	
	$('.chat-message button').click(function(){
		var input = $(this).parent().siblings('input[type=text]');		
		if(input.val() != ''){
			add_message('You','img/demo/av1.jpg',input.val(),true);
		} else {
			$('.input-box').addClass('has-error');
		}
	});
	
	$('.chat-message input').keypress(function(e){
		if($(this).val() != '') $('.input-box').removeClass('has-error');
		if(e.which == 13) {	
			if($(this).val() != ''){
				add_message('You','img/demo/av1.jpg',$(this).val(),true);
			} else {
				$('.input-box').addClass('has-error');
			}		
		}
	});
	
	setTimeout(function(){
			add_message('Neytiri','img/demo/av2.jpg','I have a problem. My computer not work!')
		},'1');
	setTimeout(function(){
			add_message('Cartoon Man','img/demo/av3.jpg','Turn off and turn on your computer then see result.')
		},'4000');
	setTimeout(function(){
            remove_user('neytiri','Neytiri')
        },'6000');
   	var i = 0;
	function add_message(name,img,msg,clear) {
		i = i + 1;
		var  inner = $('#chat-messages-inner');
		var time = new Date();
		var hours = time.getHours();
		var minutes = time.getMinutes();
		if(hours < 10) hours = '0' + hours;
		if(minutes < 10) minutes = '0' + minutes;
		var id = 'msg-'+i;
        var idname = name.replace(' ','-').toLowerCase();
		inner.append('<p id="'+id+'" class="user-'+idname+'"><img src="'+img+'" alt="" />'
										+'<span class="msg-block"><strong>'+name+'</strong> <span class="time">- '+hours+':'+minutes+'</span>'
										+'<span class="msg">'+msg+'</span></span></p>');
		$('#'+id).fadeOut(0).addClass('show');
		if(clear) {
			$('.input-box').removeClass('has-error');
			$('.chat-message input').val('').focus();

		}
		$('#chat-messages').animate({ scrollTop: inner.height() },1000);
	}
    function remove_user(userid,name) {
        i = i + 1;
        $('.contact-list li#user-'+userid).addClass('offline').delay(1000).slideUp(800,function(){
            $(this).remove();
        });
        var  inner = $('#chat-messages-inner');
        var id = 'msg-'+i;
        inner.append('<p class="offline al" id="'+id+'"><span>User <a href="#">@'+name+'</a> left the chat</span></p>');
        $('#'+id).fadeOut(0).addClass('show');
    }
});
