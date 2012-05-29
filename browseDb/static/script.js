$(document).ready(function() {
	function addEss() {
		var a = $(this);
		var current = a.html();
		a.html(current + 's'); 
	}
	function removeEss() {
		var a = $(this);
		var current = a.html();
		a.html(current.slice(0, current.length-1));
	}
	$('TH A').hover(addEss, removeEss);
});