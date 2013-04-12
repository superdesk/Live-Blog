define(['utils/utf8'],function(utf8){
	str = function(str){
		this.init(str);
	}
	str.format = function(str) {
		var idx = 0,
			arg = Array.prototype.slice.call(arguments);
			arg.shift();
		if (arg.length == 1 && typeof arg[0] == 'object')
			arg = arg[0];
		return str.replace(/%?%(?:\(([^\)]+)\))?([disr])/g, function(all, name, type) {
		  if (all[0] == all[1]) return all.substring(1);
		  var value = arg[name || idx++];		  
		  if(typeof value === 'undefined') {
			return all;
		  }
		  return (type == 'i' || type == 'd') ? +value : utf8.decode(value);
		});
	};
	str.prototype = {
		init: function(str) {
			this.str = str;
		},
		format: function() {
			var arguments = Array.prototype.slice.call(arguments);
			arguments.unshift(this.str);
			return str.format.apply(this, arguments);
		},
		toString: function() {
			return utf8.decode(this.str);
		}
	};
	return str;
});