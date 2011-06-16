/*
 * jQuery  Plugin jQPOOOP v 1.0.16
 * http://www.dieroboter.com/jQPOOOP/
 *
 * Copyright (c) 2009 Esteban Martin Gimenez
 *http://www.dieroboter.com
 * Dual licensed under the MIT and GPL licenses.
 *Email:jqpooop@gmail.com
 * Date: 2009-08-12 20:42:16 
 * Revision: 25
 */
 
(function($) {

$.fn.jqpooop = function(){


	
    this.each( function(){
			alert(this);
    });
}

$.fn.jqpooop.options_default = {
		 Unique:true,
		 Top:0,
		 Left:0,
		 Mensaje:"Ninguno",
		 Position:"absolute",
		 Ajax:" ",
		 Id:"Id",
		 Center:"true",
		 Width:400,
		 Height:250,
		 Headmsg:"Alert message"
	},

$.extend({
	'load':function(urlajax){
		
		$.ajax({
			'url':urlajax,
			'cache': false,
			'dataType': 'html',
			'type':'GET',
			success: function(msg)
			{
				//<a href="" class="accept"><span>Aceptar</span></a>
				$('<div id="'+ opc.Id +'" class="popup"><h6>'+opc.Headmsg+'</h6><button id="botonpop'+ opc.Id +'" onclick="$(this).parent().remove()"><img src="imgs/close.gif"/></button><p>'+ msg +'</p></div>').appendTo(document.body);
				var w = window.innerWidth ||document.documentElement.clientWidth || document.body.clientWidth;
				var h = window.innerHeight ||document.documentElement.clientHeight || document.body.clientHeight;
				w1 =(w/2) - (opc.Width/2); 
				h1 =(h/2) - (opc.Height/2);
				$('#'+opc.Id).css("top",h1+"px");
				$('#'+opc.Id).css("left",w1+"px");
				$('#'+opc.Id).css("display","");
				$('#'+opc.Id).css("z-index","1000");
				$('#'+opc.Id).css("position","absolute");
			}
		})
	},
'msg':function(msg){

			$('<div id="'+ opc.Id +'" class="popup"><h6>'+opc.Headmsg+'</h6><button id="botonpop'+ opc.Id +'" onclick="$(this).parent().remove()"><img src="imgs/close.gif"/></button><p>'+ msg +'</p><a href="" class="accept"><span>Aceptar</span></a></div>').appendTo(document.body);
			var w = window.innerWidth ||document.documentElement.clientWidth || document.body.clientWidth;
			var h = window.innerHeight ||document.documentElement.clientHeight || document.body.clientHeight;
			w1 =(w/2) - (opc.Width/2);
			h1 =(h/2) - (opc.Height/2);
			$('#'+opc.Id).css("top",h1+"px");
			$('#'+opc.Id).css("left",w1+"px");
			$('#'+opc.Id).css("display","");
			$('#'+opc.Id).css("z-index","1000");
			$('#'+opc.Id).css("position","absolute");
		
}	
	
	
});

$.jqpooop=function(options_user)
	{

		opc = $.extend( $.fn.jqpooop.options_default,options_user );

	
		if(opc.Unique==true && $('#'+opc.Id).length)
			{		
				return false;
			}
				
		if(opc.Ajax!=''){	
			this.load(opc.Ajax);	
				return false;
			}
		
		this.msg(opc.Mensaje);	
				return false;
	},

$.close=function(options_user)
	{
		opc = $.extend( $.fn.jqpooop.options_default,options_user );
		$('#'+opc.Id).remove();
	}

})(jQuery);
