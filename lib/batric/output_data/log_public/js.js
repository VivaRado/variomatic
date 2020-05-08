$(function(){

	$(".glyph").each(function () {
		
		console.log($(this).find(".glyph_info .init_info").text())
		$(this).find(".glyph_info").append("<code></code>")
		p(pprint( $(this).find(".glyph_info .init_info").text()),$(this).find(".glyph_info code"))
		
		$(this).find(".glyph_info .init_info").hide()

		console.log(pprint( $(this).find(".glyph_info").text()))
		
	});
});