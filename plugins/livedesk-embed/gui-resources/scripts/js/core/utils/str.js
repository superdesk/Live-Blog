define(['utils/utf8'],function(utf8){
	str = function(str){
		this.init(str);
	}
	str.prototype = {
		init: function(str) {
			this.str = str;
		},	
		format: function() {
			var arg = arguments, idx = 0;
			if (arg.length == 1 && typeof arg[0] == 'object')
				arg = arg[0];
			return utf8.decode(this.str.replace(/%?%(?:\(([^\)]+)\))?([disr])/g, function(all, name, type) {
			  if (all[0] == all[1]) return all.substring(1);
			  var value = arg[name || idx++];		  
			  if(typeof value === 'undefined') {
				return all;
			  }
			  return (type == 'i' || type == 'd') ? +value : value;
			}));
		},
		toString: function() {
			return utf8.decode(this.str);
		}
	};
	return str;
});