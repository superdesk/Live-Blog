define(function(){
	encodeURL = function(str){
		var returnString = encodeURIComponent(str).replace(/'/g, "%27").replace(/~/g, "%7E").replace(/!/g, "%21").replace(/\*/g, "%2A").replace(/\(/g, "%28").replace(/\)/g, "%29");
		return returnString;
	}
});