(function(s){
	typeof(lgaId)!=='undefined' && s.val(lgaId);
	!!s.chosen && s.chosen();
})($('select#lga-select'));
