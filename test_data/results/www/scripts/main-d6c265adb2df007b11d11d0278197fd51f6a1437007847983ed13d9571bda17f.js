/*= require decloud */
/*= require jquery */
/*= require jquery-ui */
/*= require decloud-publiching */


[%= requirejs_config %]
[%= requirejs_main %]
	$("div.greeting").text("Hello");
[%= end %]