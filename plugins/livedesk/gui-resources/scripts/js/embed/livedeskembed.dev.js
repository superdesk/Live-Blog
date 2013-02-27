window.livedesk._ = function(key){
	if(window.livedesk.i18n && window.livedesk.i18n[key] !== undefined) {
		return window.livedesk.i18n[key];
	}
	return key;
};
window.livedesk.loadGizmo = function(giveBack$) {    
    var self = this;
(function($)
    {
str = function(str){
	this.init(str);
}
str.format = function(str) {
	var arg = arguments, idx = 1;
	if (arg.length == 2 && typeof arg[1] == 'object')
		arg = arg[1];
	return str.replace(/%?%(?:\(([^\)]+)\))?([disr])/g, function(all, name, type) {
	  if (all[0] == all[1]) return all.substring(1);
	  var value = arg[name || idx++];
	  if(typeof value === 'undefined') {
		return all;
	  }
	  return (type == 'i' || type == 'd') ? +value : value; 
	});
};
str.prototype = {
	init: function(str) {
		this.str = str;
	},	
	format: function() {
		return str.format(this.str);
	},
	toString: function() {
		return this.str;
	}
};
/*
* Add integers, wrapping at 2^32. This uses 16-bit operations internally
* to work around bugs in some JS interpreters.
*/
function safe_add(x, y) {
	var lsw = (x & 0xFFFF) + (y & 0xFFFF),
		msw = (x >> 16) + (y >> 16) + (lsw >> 16);
	return (msw << 16) | (lsw & 0xFFFF);
}

/*
* Bitwise rotate a 32-bit number to the left.
*/
function bit_rol(num, cnt) {
	return (num << cnt) | (num >>> (32 - cnt));
}

/*
* These functions implement the four basic operations the algorithm uses.
*/
function md5_cmn(q, a, b, x, s, t) {
	return safe_add(bit_rol(safe_add(safe_add(a, q), safe_add(x, t)), s), b);
}
function md5_ff(a, b, c, d, x, s, t) {
	return md5_cmn((b & c) | ((~b) & d), a, b, x, s, t);
}
function md5_gg(a, b, c, d, x, s, t) {
	return md5_cmn((b & d) | (c & (~d)), a, b, x, s, t);
}
function md5_hh(a, b, c, d, x, s, t) {
	return md5_cmn(b ^ c ^ d, a, b, x, s, t);
}
function md5_ii(a, b, c, d, x, s, t) {
	return md5_cmn(c ^ (b | (~d)), a, b, x, s, t);
}

/*
* Calculate the MD5 of an array of little-endian words, and a bit length.
*/
function binl_md5(x, len) {
	/* append padding */
	x[len >> 5] |= 0x80 << ((len) % 32);
	x[(((len + 64) >>> 9) << 4) + 14] = len;

	var i, olda, oldb, oldc, oldd,
		a =  1732584193,
		b = -271733879,
		c = -1732584194,
		d =  271733878;

	for (i = 0; i < x.length; i += 16) {
		olda = a;
		oldb = b;
		oldc = c;
		oldd = d;

		a = md5_ff(a, b, c, d, x[i],       7, -680876936);
		d = md5_ff(d, a, b, c, x[i +  1], 12, -389564586);
		c = md5_ff(c, d, a, b, x[i +  2], 17,  606105819);
		b = md5_ff(b, c, d, a, x[i +  3], 22, -1044525330);
		a = md5_ff(a, b, c, d, x[i +  4],  7, -176418897);
		d = md5_ff(d, a, b, c, x[i +  5], 12,  1200080426);
		c = md5_ff(c, d, a, b, x[i +  6], 17, -1473231341);
		b = md5_ff(b, c, d, a, x[i +  7], 22, -45705983);
		a = md5_ff(a, b, c, d, x[i +  8],  7,  1770035416);
		d = md5_ff(d, a, b, c, x[i +  9], 12, -1958414417);
		c = md5_ff(c, d, a, b, x[i + 10], 17, -42063);
		b = md5_ff(b, c, d, a, x[i + 11], 22, -1990404162);
		a = md5_ff(a, b, c, d, x[i + 12],  7,  1804603682);
		d = md5_ff(d, a, b, c, x[i + 13], 12, -40341101);
		c = md5_ff(c, d, a, b, x[i + 14], 17, -1502002290);
		b = md5_ff(b, c, d, a, x[i + 15], 22,  1236535329);

		a = md5_gg(a, b, c, d, x[i +  1],  5, -165796510);
		d = md5_gg(d, a, b, c, x[i +  6],  9, -1069501632);
		c = md5_gg(c, d, a, b, x[i + 11], 14,  643717713);
		b = md5_gg(b, c, d, a, x[i],      20, -373897302);
		a = md5_gg(a, b, c, d, x[i +  5],  5, -701558691);
		d = md5_gg(d, a, b, c, x[i + 10],  9,  38016083);
		c = md5_gg(c, d, a, b, x[i + 15], 14, -660478335);
		b = md5_gg(b, c, d, a, x[i +  4], 20, -405537848);
		a = md5_gg(a, b, c, d, x[i +  9],  5,  568446438);
		d = md5_gg(d, a, b, c, x[i + 14],  9, -1019803690);
		c = md5_gg(c, d, a, b, x[i +  3], 14, -187363961);
		b = md5_gg(b, c, d, a, x[i +  8], 20,  1163531501);
		a = md5_gg(a, b, c, d, x[i + 13],  5, -1444681467);
		d = md5_gg(d, a, b, c, x[i +  2],  9, -51403784);
		c = md5_gg(c, d, a, b, x[i +  7], 14,  1735328473);
		b = md5_gg(b, c, d, a, x[i + 12], 20, -1926607734);

		a = md5_hh(a, b, c, d, x[i +  5],  4, -378558);
		d = md5_hh(d, a, b, c, x[i +  8], 11, -2022574463);
		c = md5_hh(c, d, a, b, x[i + 11], 16,  1839030562);
		b = md5_hh(b, c, d, a, x[i + 14], 23, -35309556);
		a = md5_hh(a, b, c, d, x[i +  1],  4, -1530992060);
		d = md5_hh(d, a, b, c, x[i +  4], 11,  1272893353);
		c = md5_hh(c, d, a, b, x[i +  7], 16, -155497632);
		b = md5_hh(b, c, d, a, x[i + 10], 23, -1094730640);
		a = md5_hh(a, b, c, d, x[i + 13],  4,  681279174);
		d = md5_hh(d, a, b, c, x[i],      11, -358537222);
		c = md5_hh(c, d, a, b, x[i +  3], 16, -722521979);
		b = md5_hh(b, c, d, a, x[i +  6], 23,  76029189);
		a = md5_hh(a, b, c, d, x[i +  9],  4, -640364487);
		d = md5_hh(d, a, b, c, x[i + 12], 11, -421815835);
		c = md5_hh(c, d, a, b, x[i + 15], 16,  530742520);
		b = md5_hh(b, c, d, a, x[i +  2], 23, -995338651);

		a = md5_ii(a, b, c, d, x[i],       6, -198630844);
		d = md5_ii(d, a, b, c, x[i +  7], 10,  1126891415);
		c = md5_ii(c, d, a, b, x[i + 14], 15, -1416354905);
		b = md5_ii(b, c, d, a, x[i +  5], 21, -57434055);
		a = md5_ii(a, b, c, d, x[i + 12],  6,  1700485571);
		d = md5_ii(d, a, b, c, x[i +  3], 10, -1894986606);
		c = md5_ii(c, d, a, b, x[i + 10], 15, -1051523);
		b = md5_ii(b, c, d, a, x[i +  1], 21, -2054922799);
		a = md5_ii(a, b, c, d, x[i +  8],  6,  1873313359);
		d = md5_ii(d, a, b, c, x[i + 15], 10, -30611744);
		c = md5_ii(c, d, a, b, x[i +  6], 15, -1560198380);
		b = md5_ii(b, c, d, a, x[i + 13], 21,  1309151649);
		a = md5_ii(a, b, c, d, x[i +  4],  6, -145523070);
		d = md5_ii(d, a, b, c, x[i + 11], 10, -1120210379);
		c = md5_ii(c, d, a, b, x[i +  2], 15,  718787259);
		b = md5_ii(b, c, d, a, x[i +  9], 21, -343485551);

		a = safe_add(a, olda);
		b = safe_add(b, oldb);
		c = safe_add(c, oldc);
		d = safe_add(d, oldd);
	}
	return [a, b, c, d];
}

/*
* Convert an array of little-endian words to a string
*/
function binl2rstr(input) {
	var i,
		output = '';
	for (i = 0; i < input.length * 32; i += 8) {
		output += String.fromCharCode((input[i >> 5] >>> (i % 32)) & 0xFF);
	}
	return output;
}

/*
* Convert a raw string to an array of little-endian words
* Characters >255 have their high-byte silently ignored.
*/
function rstr2binl(input) {
	var i,
		output = [];
	output[(input.length >> 2) - 1] = undefined;
	for (i = 0; i < output.length; i += 1) {
		output[i] = 0;
	}
	for (i = 0; i < input.length * 8; i += 8) {
		output[i >> 5] |= (input.charCodeAt(i / 8) & 0xFF) << (i % 32);
	}
	return output;
}

/*
* Calculate the MD5 of a raw string
*/
function rstr_md5(s) {
	return binl2rstr(binl_md5(rstr2binl(s), s.length * 8));
}

/*
* Calculate the HMAC-MD5, of a key and some data (raw strings)
*/
function rstr_hmac_md5(key, data) {
	var i,
		bkey = rstr2binl(key),
		ipad = [],
		opad = [],
		hash;
	ipad[15] = opad[15] = undefined;
	if (bkey.length > 16) {
		bkey = binl_md5(bkey, key.length * 8);
	}
	for (i = 0; i < 16; i += 1) {
		ipad[i] = bkey[i] ^ 0x36363636;
		opad[i] = bkey[i] ^ 0x5C5C5C5C;
	}
	hash = binl_md5(ipad.concat(rstr2binl(data)), 512 + data.length * 8);
	return binl2rstr(binl_md5(opad.concat(hash), 512 + 128));
}

/*
* Convert a raw string to a hex string
*/
function rstr2hex(input) {
	var hex_tab = '0123456789abcdef',
		output = '',
		x,
		i;
	for (i = 0; i < input.length; i += 1) {
		x = input.charCodeAt(i);
		output += hex_tab.charAt((x >>> 4) & 0x0F) +
			hex_tab.charAt(x & 0x0F);
	}
	return output;
}

/*
* Encode a string as utf-8
*/
function str2rstr_utf8(input) {
	return unescape(encodeURIComponent(input));
}

/*
* Take string arguments and return either raw or hex encoded strings
*/
function raw_md5(s) {
	return rstr_md5(str2rstr_utf8(s));
}
function hex_md5(s) {
	return rstr2hex(raw_md5(s));
}
function raw_hmac_md5(k, d) {
	return rstr_hmac_md5(str2rstr_utf8(k), str2rstr_utf8(d));
}
function hex_hmac_md5(k, d) {
	return rstr2hex(raw_hmac_md5(k, d));
}

function md5(string, key, raw) {
	if (!key) {
		if (!raw) {
			return hex_md5(string);
		} else {
			return raw_md5(string);
		}
	}
	if (!raw) {
		return hex_hmac_md5(key, string);
	} else {
		return raw_hmac_md5(key, string);
	}
}

$.md5 = md5;
var gravatar = {
	url: '//gravatar.com/avatar/%(md5)s?r=%(rate)s&s=%(size)s&d=%(default)s&%(forcedefault)s',
	defaults: {
		rate: 'pg',
		size: 48,
		"default": encodeURIComponent('images/avatar_default_collaborator.png'),
		forcedefault: '',
		key: 'Avatar',
		needle: 'Person.EMail'
	},
	parse: function(data, needle) {
		if(!data) return;
		if(!needle) needle = this.defaults.needle;
		var self = this,
		arr = needle.split('.'),
		searchKey = arr[0],
		searchValue = arr[1];
		$.each(data, function(key, value){
			if((key === searchKey) && (searchValue!==undefined) && ( $.isDefined(value[searchValue]))) {
				this[self.defaults.key] = self.get(value[searchValue]);
			}
			if($.isObject(value) || $.isArray(value)) {
				self.parse(value,needle);
			}
		});
		return data;
	},
	get: function(value) {
		var self = this;
		if($.type(value) !== 'string')
			return value;
		return str.format(self.url,$.extend({}, self.defaults, { md5: $.md5($.trim(value.toLowerCase()))}));
	}
};
$.avatar  = gravatar;
/*
 * Date Format 1.2.3
 * (c) 2007-2009 Steven Levithan <stevenlevithan.com>
 * MIT license
 *
 * Includes enhancements by Scott Trenda <scott.trenda.net>
 * and Kris Kowal <cixar.com/~kris.kowal/>
 *
 * Accepts a date, a mask, or a date and a mask.
 * Returns a formatted version of the given date.
 * The date defaults to the current date/time.
 * The mask defaults to dateFormat.masks.default.
 */

var dateFormat = function () {
	var	token = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
		timezone = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
		timezoneClip = /[^-+\dA-Z]/g,
		pad = function (val, len) {
			val = String(val);
			len = len || 2;
			while (val.length < len) val = "0" + val;
			return val;
		};

	// Regexes and supporting functions are cached through closure
	return function (date, mask, utc) {
		var dF = dateFormat;

		// You can't provide utc if you skip other args (use the "UTC:" mask prefix)
		if (arguments.length == 1 && Object.prototype.toString.call(date) == "[object String]" && !/\d/.test(date)) {
			mask = date;
			date = undefined;
		}

		// Passing date through Date applies Date.parse, if necessary
		date = date ? new Date(date) : new Date;
		if (isNaN(date)) throw SyntaxError("invalid date");

		mask = String(dF.masks[mask] || mask || dF.masks["default"]);

		// Allow setting the utc argument via the mask
		if (mask.slice(0, 4) == "UTC:") {
			mask = mask.slice(4);
			utc = true;
		}

		var	_ = utc ? "getUTC" : "get",
			d = date[_ + "Date"](),
			D = date[_ + "Day"](),
			m = date[_ + "Month"](),
			y = date[_ + "FullYear"](),
			H = date[_ + "Hours"](),
			M = date[_ + "Minutes"](),
			s = date[_ + "Seconds"](),
			L = date[_ + "Milliseconds"](),
			o = utc ? 0 : date.getTimezoneOffset(),
			flags = {
				d:    d,
				dd:   pad(d),
				ddd:  dF.i18n.dayNames[D],
				dddd: dF.i18n.dayNames[D + 7],
				m:    m + 1,
				mm:   pad(m + 1),
				mmm:  dF.i18n.monthNames[m],
				mmmm: dF.i18n.monthNames[m + 12],
				yy:   String(y).slice(2),
				yyyy: y,
				h:    H % 12 || 12,
				hh:   pad(H % 12 || 12),
				H:    H,
				HH:   pad(H),
				M:    M,
				MM:   pad(M),
				s:    s,
				ss:   pad(s),
				l:    pad(L, 3),
				L:    pad(L > 99 ? Math.round(L / 10) : L),
				t:    H < 12 ? "a"  : "p",
				tt:   H < 12 ? "am" : "pm",
				T:    H < 12 ? "A"  : "P",
				TT:   H < 12 ? "AM" : "PM",
				Z:    utc ? "UTC" : (String(date).match(timezone) || [""]).pop().replace(timezoneClip, ""),
				o:    (o > 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),
				S:    ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10]
			};

		return mask.replace(token, function ($0) {
			return $0 in flags ? flags[$0] : $0.slice(1, $0.length - 1);
		});
	};
}();

// Some common format strings
dateFormat.masks = {
	"default":      "ddd mmm dd yyyy HH:MM:ss",
	shortDate:      "m/d/yy",
	mediumDate:     "mmm d, yyyy",
	longDate:       "mmmm d, yyyy",
	fullDate:       "dddd, mmmm d, yyyy",
	shortTime:      "h:MM TT",
	mediumTime:     "h:MM:ss TT",
	longTime:       "h:MM:ss TT Z",
	isoDate:        "yyyy-mm-dd",
	isoTime:        "HH:MM:ss",
	isoDateTime:    "yyyy-mm-dd'T'HH:MM:ss",
	isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"
};

// Internationalization strings
dateFormat.i18n = {
	dayNames: [
		"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat",
		"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
	],
	monthNames: [
		"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
		"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
	]
};
if(window.livedesk.i18n && window.livedesk.i18n['day_names'] !== undefined) {
	dateFormat.i18n.dayNames = window.livedesk.i18n.day_names;
}
if(window.livedesk.i18n && window.livedesk.i18n['month_names'] !== undefined) {
	dateFormat.i18n.monthNames = window.livedesk.i18n.month_names;
}

// For convenience...
Date.prototype.format = function (mask, utc) {
	return dateFormat(this, mask, utc);
};

if(!Array.isArray) {
  Array.isArray = function (vArg) {
    return Object.prototype.toString.call(vArg) === "[object Array]";
  };
}

if (!Function.prototype.bind) {
    Function.prototype.bind = function (oThis) {
        if (typeof this !== "function") {
            // closest thing possible to the ECMAScript 5 internal IsCallable function
            throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
        }

        var aArgs = Array.prototype.slice.call(arguments, 1),
                fToBind = this,
                fNOP = function () {},
                fBound = function () {
                    return fToBind.apply(this instanceof fNOP
                                                                    ? this
                                                                    : oThis,
                                                            aArgs.concat(Array.prototype.slice.call(arguments)));
                };

        fNOP.prototype = this.prototype;
        fBound.prototype = new fNOP();

        return fBound;
    };
}
if (!String.prototype.trim) {
        String.prototype.trim = function() {
                var that = this.replace(/^\s\s*/, ''),
                        ws = /\s/,
                        i = that.length;
                while (ws.test(that.charAt(--i)));
                return that.slice(0, i + 1);
        }
}
var initializing = false;
      // The base Class implementation (does nothing)
      this.Class = function(){};
      
      // Create a new Class that inherits from this class
      Class.extend = function(prop, options) {   
        // Instantiate a base class (but only create the instance,
        // don't run the init constructor)
        initializing = true;
        var prototype = new this();
        initializing = false;
        
        // Copy the properties over onto the new prototype
        for (var name in prop) {
          // Check if we're overwriting an existing function
          prototype[name] = prop[name];
        }
        
        // The dummy class constructor
        function Class() {
          // All construction is actually done in the init method
          if ( !initializing && ( this._constructor || this._construct ) )
              try
              { 
                  var constructor = this._construct || this._constructor; 
                  return constructor.apply(this, arguments);
              }
              catch(e){}
        }
        
        // Populate our constructed prototype object
        Class.prototype = prototype;
        
        // Enforce the constructor to be what we expect
        Class.prototype.constructor = Class;
    
        // And make this class extendable
        Class.extend = arguments.callee;

        return Class;
        
      }
function compareObj(x, y)
{
  var p;
  if( (typeof(x)=='undefined') || (typeof(y)=='undefined') ) {return true;}
  for(p in y) {
	  if(typeof(x[p])=='undefined') {return true;}
  }

  for(p in x) {
	  if(typeof(y[p])=='undefined') {return true;}
  }

  for(p in y) {
	  if (y[p]) {
		  switch(typeof(y[p])) {
			  case 'object':
				  if (compareObj(y[p],x[p])) {return true;}break;
			  case 'function':
				  if (typeof(x[p])=='undefined' ||
					  (y[p].toString() != x[p].toString()))
					  return true;
				  break;
			  default:
				  if (y[p] != x[p]) {return true;}
		  }
	  } else {
		  if (x[p])
			  return true;
	  }
  }

  return false;
}

var Register = function(){},
Model = function(data){},
Uniq = function()
{
	this.items = {};
	//$(this.instances).trigger('garbage');
	//this.instances.push(this);
},
Collection = function(){},

Url = Class.extend
({
	_construct: function(arg) 
	{
		this.data = !this.data ? {root: ''} : this.data;
		switch( $.type(arg) )
		{
			case 'string':
				this.data.url = arg;
				break;
			case 'array':
				this.data.url = arg[0];
				if(arg[1] !== undefined) this.data.xfilter = url[0];
				break;
			case 'object': // options, same technique as above
				this.data.url = arg.url
				if(arg.xfilter !== undefined) this.data.xfilter = arg.xfilter;
				break;
		}
		return this;
	},
	xfilter: function() 
	{
		this.data.xfilter = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];
		return this;
	},
	root: function(root) 
	{
		this.data.root = root;
		return this;
	},
	get: function()
	{
		return this.data.root + this.data.url;
	},
	order: function(key, direction) 
	{
		this.data.order = direction+'='+key;
		return this;
	},
	filter: function(key, value) 
	{
		this.data.filter = key+'='+value;
		return this;
	},
	decorate: function(format)
	{
		this.data.url = format.replace(/(%s)/g, this.data.url);
	},
	options: function() 
	{
		var options = {};
		if(this.data.xfilter)
			options.headers = {'X-Filter': this.data.xfilter};
		return options;
	}
}),
Sync =
{
	request: function(source)
	{
		var self = this,
			reqFnc = function(data, predefinedOptions, userOptions)
			{
								$.support.cors = true;
				var a;
				if( source instanceof Url ) 
				{
					var options = $.extend(true, {}, predefinedOptions, self.options, userOptions, {data: data}, source.options());
					a = $.ajax(self.href(source.get()), options);
				} 
				else 
				{
					var options = $.extend(true, {}, predefinedOptions, self.options, userOptions, {data: data});
					a = $.ajax(self.href(source), options);
				}
				self.reset();
				
				options.fail && a.fail(options.fail);
				options.done && a.done(options.done);
				options.always && a.always(options.always);
				return a;
			};

		return {

			read: function(userOptions){return reqFnc({}, self.readOptions, userOptions);},

			update: function(data, userOptions){return reqFnc(data, self.updateOptions, userOptions);},

			insert: function(data, userOptions){return reqFnc(data, self.insertOptions, userOptions);},

			remove: function(userOptions){return reqFnc({}, self.removeOptions, userOptions);}
		};
	},
	href: function(source){return source;},
	reset: $.noop,
	// bunch of options for each type of operation
	options: {},
	readOptions: {dataType: 'json', type: 'get', headers: {'Accept' : 'text/json'}},
	updateOptions: {type: 'post', headers: {'X-HTTP-Method-Override': 'PUT'}},
	insertOptions: {dataType: 'json', type: 'post'},
	removeOptions: {type: 'get', headers: {'X-HTTP-Method-Override': 'DELETE'}}
};

var uniqueIdCounter = 0;
Model.prototype =
{
	_changed: false,
	_new: false,
	defaults: {},
	data: {},
	/*!
	 * constructor
	 */
	_construct: function(data, options)
	{
		this._clientId = uniqueIdCounter++;
		this.data = {};
		this.parseHash(data);
		this._new = true;
		var self = this.pushUnique ? this.pushUnique() : this;
		self._forDelete = false;
		self.clearChangeset();
		self._clientHash = null;
		if( options && typeof options == 'object' ) $.extend(self, options);
		if( typeof data == 'object' ) {
			self._parse(data);
		}
		self._setExpiration();
		if(self.isDeleted()){
			//console.log('pull remove');
			self._remove();
		}
		else if(!$.isEmptyObject(self.changeset)) {
			//console.log('pull update: ',$.extend({},self.changeset));
			self.triggerHandler('update', self.changeset).clearChangeset();
		}
		else {
			//console.log('pull read');
			self.clearChangeset().triggerHandler('read');
		}
		return self;
	},
	/*!
	 * adapter for data sync
	 */
	syncAdapter: Sync,
	/*!
	 * @param format
	 */
	feed: function(format, deep, fromData)
	{
		var ret = {},
			feedData = fromData ? fromData : this.data;
		for( var i in feedData )
			ret[i] = feedData[i] instanceof Model ?
					(deep ? feedData[i].feed(deep) : feedData[i].relationHash() || feedData[i].hash()) :
					feedData[i];
		return ret;
	},
	/*!
	 * data sync call
	 */
	sync: function()
	{
		//console.log('sync');
		var self = this, ret = $.Deferred(), dataAdapter = function(){return self.syncAdapter.request.apply(self.syncAdapter, arguments);};
		this.hash();
		// trigger an event before sync
		self.triggerHandler('sync');

		if( this._forDelete ) {// handle delete
			//console.log('delete');
			return dataAdapter(arguments[0] || this.href).remove().done(function()
			{
				self._remove();
			});
		}
		if( this._clientHash ) // handle insert
		{
			//console.log('insert');
			var href = arguments[0] || this.href;
			return dataAdapter(href).insert(this.feed()).done(function(data)
			{
				self._changed = false;
				self._parse(data);
				self._uniq && self._uniq.replace(self._clientHash, self.hash(), self);
				self._clientHash = null;
				self.triggerHandler('insert')
					.Class.triggerHandler('insert', self);
			});
		}

		if( this._changed ) {// if changed do an update on the server and return
			//console.log('update');
			if(!$.isEmptyObject(this.changeset)) {
				ret = (this.href && dataAdapter(this.href)
						.update(arguments[1] ? this.feed() : this.feed('json', false, this.changeset))
						.done(function()
				{
					self.triggerHandler('update', self.changeset).clearChangeset();
				}));
			}
		}
		else {
			if( !(arguments[0] && arguments[0].force) && this.exTime && (  this.exTime > new Date) ) {
				if(!self.isDeleted()){
					self.triggerHandler('update');
				}
			}
			else { 
			// simply read data from server
			ret = (this.href && dataAdapter(this.href).read(arguments[0]).done(function(data)
			{
				//console.log('Pull: ',$.extend({},data));
				self._parse(data);
				/**
				 * delete should come first of everything
				 * caz it can be some update data or read data that is telling is a deleted model.
				 */
				if(self.isDeleted()){
					//console.log('pull remove');
					self._remove();
				}
				else if(!$.isEmptyObject(self.changeset)) {
					//console.log('pull update: ',$.extend({},self.changeset));
					self.triggerHandler('update', self.changeset).clearChangeset();
				}
				else {
					//console.log('pull read');
					self.clearChangeset().triggerHandler('read');
				}
			}));
			}
		}
		this._setExpiration();
		return ret;
	},
	_setExpiration: function()
	{
		this.exTime = new Date;
		this.exTime.setSeconds(this.exTime.getSeconds() + 5);
	},
	_remove: function()
	{
		this.triggerHandler('delete');
		this._uniq && this._uniq.remove(this.hash());
		//delete this;
	},
	remove: function()
	{
		this._forDelete = true;
		return this;
	},
	isDeleted: function()
	{
		return this._forDelete;
	},
	/*!
	 * overwrite this to add other logic upon parse complex type data
	 */
	modelDataBuild: function(model)
	{
		return model
	},
	/**
	 * should be override by implementation
	 */
	parse: function(data)
	{
		return data;
	},
	/*!
	 * @param data the data to parse into the model
	 */
	_parse: function(data)
	{
		if(data instanceof Model) {
			data = data.data;
		} else {
			data = this.parse(data);
		}		
		if(data._parsed) {
			return;
		}
		for( var i in data )
		{
			if( this.defaults[i] ) switch(true)
			{
				case (typeof this.defaults[i] === 'function') && (this.data[i] === undefined): // a model or collection constructor
					
					var newModel = this.modelDataBuild(new this.defaults[i](data[i]));
					if( !this._new && (newModel != this.data[i]) && !(newModel instanceof Collection) )
						this.changeset[i] = newModel;
					this.data[i] = newModel;

					// fot model w/o href, need to make a collection since it's obviously
					// an existing one and we don't need a new one
					// TODO instanceof Model?
					!data[i].href && this.data[i].relationHash && this.data[i].relationHash(data[i]);

					continue;
					break;

				case $.isArray(this.defaults[i]): // a collection
					this.data[i] = this.modelDataBuild(new Collection(this.defaults[i][0], data[i].href));
					delete this.data[i];
					continue;
					break;

				case this.defaults[i] instanceof Collection: // an instance of some colelction/model
				case this.defaults[i] instanceof Model:
					this.data[i] = this.defaults[i];
					continue;
					break;
			}
			else if( !this._new ) 
			{
				if( $.type(data[i]) === 'object' )
				{
					if(compareObj(this.data[i], data[i]))
						this.changeset[i] = data[i];
				}
				else if( this.data[i] != data[i] )
				{
					this.changeset[i] = data[i];
				}
			}
			if( $.type(data[i]) === 'object' && $.type(this.data[i]) === 'object' )
				$.extend(true, this.data[i], data[i]);
			else
				this.data[i] = data[i];
		}
		this._new = false;
		data._parsed = true;
	},
	parseHash: function(data)
	{
		if(data instanceof Model)
			return this;
		if( typeof data == 'string' )
			this.href = data;
		else if( data && data.href !== undefined) {
			this.href = data.href;
			delete data.href;
		}
		else if(data && ( data.id !== undefined) && (this.url !== undefined))
			this.href = this.url + data.id;
		return this;
	},
	clearChangeset: function()
	{
		this._changed = false
		this.changeset = {};
		return this;
	},
	get: function(key)
	{
		return this.data[key];
	},
	set: function(key, val, options)
	{
		var data = {};
		if( $.type(key) === 'string' )
			data[key] = val;
		else
		{
			data = key;
			options = val;
		}
		options = $.extend({},{silent: false}, options);
		this.clearChangeset()._parse(data);
		this._changed = true;
		if(!$.isEmptyObject(this.changeset)) {
			if(!options.silent)
				this.triggerHandler('set', this.changeset);
		}

		return this;
	},
	/*!
	 * used for new models not yet saved on the api
	 */
	_getClientHash: function()
	{
		if( !this._clientHash ) this._clientHash = "mcid-"+String(this._clientId);
		return this._clientHash;
	},
	/*!
	 * represents the formula to identify the model uniquely
	 */
	hash: function()
	{
		if( !this.href && this.data.href ) this.href = this.data.href;
		return this.data.href || this.href || this._getClientHash();
	},
	/*!
	 * used to relate models. a general standard key would suffice
	 */
	relationHash: function(val){if(val) this.data.Id = val;return this.data.Id;},
	/*!
	 * used to remove events from this model
	 */
	off: function(evt, handler)		
	{
		$(this).off(evt, handler);
		return this;
	},
	/*!
	 * used to place events on this model,
	 * scope of the call method is sent as obj argument
	 */
	on: function(evt, handler, obj)
	{
		if(obj === undefined) {
			$(this).off(evt, handler);
			$(this).on(evt, handler);
		}
		else {			
			$(this).on(evt, function(){
				handler.apply(obj, arguments);
			});
		}
		return this;
	},
	one: function(evt, handler, obj)
	{
		if(obj === undefined) {
			$(this).off(evt, handler);
			$(this).one(evt, handler);
		}
		else {			
			$(this).one(evt, function(){
				handler.apply(obj, arguments);
			});
		}
		return this;
	},
	
	/*!
	 * used to trigger model events
	 * this also calls the model method with the event name
	 */
	trigger: function(evt, data)
	{
		$(this).trigger(evt, data);
		return this;
	},
	/*!
	 * used to trigger handle of model events
	 * this doens't call any method see: trigger
	 */
	triggerHandler: function(evt, data)
	{
		$(this).triggerHandler(evt, data);
		return this;
	}
};

/*!
 * defs for unique storage of models
 */
Uniq.prototype =
{
	items: {},
	garbageTime: 1500, //300000,
	refresh: function(val)
	{
		if( !val._exTime ) val._exTime = new Date;
		val._exTime.setTime(val._exTime.getTime() + this.garbageTime);
	},
	/*!
	 *
	 */
	set: function(key, val)
	{
		var self = this;
		$(val).on('sync get get-prop set-prop', function(){self.refresh(this);});
		self.refresh(val);
		if( !this.items[key] ) this.items[key] = val;
		return this.items[key];
	},
	/*!
	 * replace a key with another key value actually
	 */
	replace: function(key, newKey, val)
	{
		delete this.items[key];
		return this.set(newKey, val);
	},
	/*!
	 *
	 */
	garbage: function()
	{
		for( var key in this.items )
		{
			if( this.items[key]._exTime && this.items[key]._exTime < new Date )
			{
				$(this.items[key]).triggerHandler('garbage');
				delete this.items[key];
			}
		}
	},
	remove: function(key)
	{
		delete this.items[key];
	}
};
// Model's base options
var options = Model.options = {}, extendFnc, cextendFnc;
Model.extend = extendFnc = function(props, options)
{
	var newly;
	newly = Class.extend.call(this, props);
	newly.extend = extendFnc;
	newly.prototype.Class = newly;
	newly.on = function(event, handler, obj)
	{
		$(newly).on(event, function(){handler.apply(obj, arguments);});
		return newly;
	};
	newly.off = function(event, handler)
	{
		$(newly).off(event, handler);
		return newly;
	};		
	newly.triggerHandler = function(event, data){$(newly).triggerHandler(event, data);};

	if(options && options.register) {
		Register[options.register] = newly;
		delete options.register;
	}
	// create a new property from original options one
	newly.prototype.options = $.extend({}, options);

	return newly;
};

Collection.prototype =
{
	_list: [],
	getList: function(){return this._list;},
	count: function(){return this._list.length;},
	_construct: function()
	{
		if( !this.model ) this.model = Model;
		this._list = [];
		this.desynced = true;
		var buildData = buildOptions = function(){void(0);},
			self = this;
		for( var i in arguments )
		{
			switch( $.type(arguments[i]) )
			{
				case 'function': // a model
					this.model = arguments[i];
					break;
				case 'string': // a data source
					this.href = arguments[i];
					break;
				case 'array': // a list of models, a function we're going to call after setting options
					buildData = (function(args){return function(){this._list = this._parse(args);}})(arguments[i]);
					break;
				case 'object': // options, same technique as above
					buildOptions = (function(args){return function(){this.options = args;if(args.href) this.href = args.href;}})(arguments[i]);
					break;
			}
		}
		// callbacks in order
		buildOptions.call(this);
		buildData.call(this);
		options = $.extend({}, {init: true}, this.options);
		options.init && this.init.apply(this, arguments);

	},
	init: function(){},
	get: function(key)
	{
		var dfd = $.Deferred(),
			self = this;
			searchKey = function()
			{
				for( var i=0; i<self._list.length; i++ )
					if( key == self._list[i].hash() || key == self._list[i].relationHash() )
						return dfd.resolve(self._list[i]);
				dfd.reject();
			};
		this.desynced && this.sync().done(function(){dfd.resolve(searchKey());}) ? dfd : searchKey();
		return dfd;
	},
	remove: function(key)
	{
		for( var i in this._list )
			if( key == this._list[i].hash() || key == this._list[i].relationHash() )
			{
				Array.prototype.splice.call(this._list, i, 1);
				break;
			}
		return this;
	},
	syncAdapter: Sync,
	/*!
	 *
	 */
	setHref: function(href)
	{
		this.href = href;
		return this;
	},
	each: function(fn){
		$.each(this._list, fn);
	},
	forwardEach: function(fn, scope){
		this._list.forEach(fn, scope);
	},
	reverseEach: function(fn, scope)
	{
		for(var i = this._list.length; i > 0; ++i) {
			fn.call(scope || this, this[i], i, this);
		}
	},
	feed: function(format, deep)
	{
		var ret = [];
		for( var i in this._list )
			ret[i] = this._list[i].feed(format, deep);
		return ret;
	},
	/*!
	 * @param options
	 */
	sync: function()
	{
		var self = this;
		return (this.href &&
			this.syncAdapter.request.call(this.syncAdapter, this.href).read(arguments[0]).done(function(data)
			{
				var data = self._parse(data), addings = [], updates = [], count = self._list.length;
				 // important or it will infiloop
				for( var i=0; i < data.length; i++ )
				{
					var model = false;
					for( var j=0; j<count; j++ ) {
						if( data[i].hash() == self._list[j].hash() )
						{
							model = data[i];
							break;
						}
					}
					if( !model ) {
						if( !data[i].isDeleted() ) {
							self._list.push(data[i]);
							addings.push(data[i]);
						} else {
							updates.push(data[i]);						
						}
					}
					else {
						updates.push(model);
						if( model.isDeleted() ) {
							model._remove();
						} else {
							model.on('delete', function(){self.remove(this.hash());})
									.on('garbage', function(){this.desynced = true;});
						}
					}
				}
				self.desynced = false;
				/**
				 * If the initial data is empty then trigger READ event
				 * else UPDATE with the changeset if there are some
				 */
				if( ( count === 0) ){
					//console.log('read');
					self.triggerHandler('read');
				} else {                    
					/**
					 * Trigger handler with changeset extraparameter as a vector of vectors,
					 * caz jquery will send extraparameters as arguments when calling handler
					 */
					//console.log('update');
					self.triggerHandler('updates', [updates]);
					self.triggerHandler('addings', [addings]);
				}
			}));
	},
	/*!
	 * overwrite this to add other logic upon parse complex type data
	 */
	modelDataBuild: function(model)
	{
		return model;
	},
	/**
	 * should be override by implementation
	 */
	parse: function(data)
	{
		var ret = data;
		if( !Array.isArray(data) ) for( i in data )
		{
			if( $.isArray(data[i]) )
			{
				ret = data[i];
				break;
			}
		}
		return ret;
	},
	
	/*!
	 *
	 */
	_parse: function(data)
	{
		if(data._parsed) {
			return data._parsed;
		}
		data = this.parse(data);
		var i,list = [], model;
		for( i in data ) {
			if(data.hasOwnProperty(i)) {
				model = new this.model(data[i]);
				model = this.modelDataBuild(model);
				list.push( model );
			}
		}
		data._parsed = list;
		return data._parsed;
	},
	insert: function(model)
	{
		this.desynced = false;
		if( !(model instanceof Model) ) model = this.modelDataBuild(new this.model(model));
		this._list.push(model);
		model.hash();
		var x = model.sync(this.href);
		return x;
	},
	/*!
	 * used to remove events from this model
	 */
	off: function(evt, handler)		
	{
		$(this).off(evt, handler);
		return this;
	},
	/*!
	 * used to place events on this model,
	 * scope of the call method is sent as obj argument
	 */
	on: function(evt, handler, obj)
	{
		if(obj === undefined) {
			$(this).off(evt, handler);
			$(this).on(evt, handler);
		}
		else {			
			$(this).on(evt, function(){
				handler.apply(obj, arguments);
			});
		}
		return this;
	},
	one: function(evt, handler, obj)
	{
		if(obj === undefined) {
			$(this).off(evt, handler);
			$(this).one(evt, handler);
		}
		else {			
			$(this).one(evt, function(){
				handler.apply(obj, arguments);
			});
		}
		return this;
	},	
	/*!
	 * used to trigger model events
	 * this also calls the model method with the event name
	 */
	trigger: function(evt, data)
	{
		$(this).trigger(evt, data);
		return this;
	},
	/*!
	 * used to trigger handle of model events
	 * this doens't call any method see: trigger
	 */
	triggerHandler: function(evt, data)
	{
		$(this).triggerHandler(evt, data);
		return this;
	}
};

Collection.extend = cextendFnc = function(props)
{
	var newly;
	newly = Class.extend.call(this, props);
	newly.extend = cextendFnc;
	if(options && options.register)
		Collection[options.register] = newly;
	return newly;
};
// view

var uniqueIdView = 0,
Render = Class.extend
({
	getProperty: function(prop)
	{
		if (!this[prop]) return null;
		return (typeof this[prop] === 'function') ? this[prop]() : this[prop];
	}
}),
View = Render.extend
({
	tagName: 'div',
	attributes: {className: '', id: ''},
	namespace: 'view',
	_constructor: function(data, options)
	{
		$.extend(this, data);
		this._clientId = uniqueIdView++;
		options = $.extend({}, {init: true, events: true, ensure: true}, options);
		options.ensure && this._ensureElement();
		options.init && this.init.apply(this, arguments);
		options.events && this.resetEvents();
	},
	_ensureElement: function()
	{
		var className = this.attributes.className,
			id = this.attributes.id,
			el ='';
		if(!$(this.el).length) {
			if($.type(this.el) === 'string') {
				if(this.el[0]=='.') {
					className = className + this.el.substr(0,1);
				}
				if(this.el[0]=='#') {
					id = this.el.substr(0,1);
				}
			}
			el = '<'+this.tagName;
			if(className !== '') {
				el = el + ' class="'+className+'"';
			}
			if(id !== '') {
				el = el + ' id="'+id+'"';
			}
			el = el + '></'+this.tagName+'>';
			this.el = $(el);
		} else
			this.el = $(this.el);
	},
	init: function(){return this;},
	resetEvents: function()
	{
		this.undelegateEvents();
		this.delegateEvents();
	},
	delegateEvents: function(events)
	{
		var self = this;
		if (!(events || (events = this.getProperty('events')))) return;
		for(var selector in events) {
			var one = events[selector];
			for(var evnt in one) {
				var other = one[evnt], sel = null, dat = {}, fn;
				if(typeof other === 'string') {
					fn  = other;
					//console.log($.type(self[fn]), ', ', this.getEvent(evnt), ', ',selector, ', ',fn);
					if($.isFunction(self[fn])) {
						$(this.el).on(this.getEvent(evnt), selector, self[fn].bind(self));
					}
				}
			}
		}
	},
	undelegateEvents: function()
	{
		$(this.el).off(this.getNamespace());
		return this;
	},		
	getEvent: function(evnt){
		return evnt + this.getNamespace();
	},
	getNamespace: function()
	{
		return '.'+this.getProperty('namespace');
	},
	render: function(){

		this.delegateEvents();
		return this;
	},
	remove: function()
	{
		$(this.el).remove();
		this.destroy();
		return this;
	},
	destroy: function()
	{
		if(this.model)
			this.model.trigger('destroy');
		if(this.collection)
			this.collection.trigger('destroy');
		return this;
	},
	checkElement: function()
	{
		//console.log('Undefined: ',(this.el === undefined));
		
		if(this.el === undefined)
			return false;
		
		//console.log('Selector: ',this.el.selector, ' length: ',($(this.el.selector).length === 1));
		
		if((this.el.selector !== undefined) && (this.el.selector != ''))
			return ($(this.el.selector).length === 1);			
		
		//console.log('Visible: ',$(this.el).is(':visible'));

		return ($(this.el).is(':visible'));
		
		//console.log('Last: ',this.el, ' length: ',($(this.el).length === 1));
		
		return ($(this.el).length === 1);
		
	},
	setElement: function(el)
	{
		this.undelegateEvents();
		var newel = $(el), prevData = this.el.data();
		this.el.replaceWith(newel);
		this.el = newel;
		this.el.data(prevData);
		this.delegateEvents();
		return this;
	},
	resetElement: function(el)
	{
			this.el = $(el);
		this._ensureElement();
		this.delegateEvents();
	}
});



var giz = {Model: Model, Collection: Collection, Sync: Sync, UniqueContainer: Uniq, View: View, Url: Url, Register: Register};
    
    var syncReset = function() // reset specific data and headers for superdesk
    {
        try
        { 
            delete this.options.headers['X-Filter'];
            this.options.data = {};
        }
        catch(e){}
    }, 
    newSync = $.extend({}, giz.Sync,
    {
        reset: syncReset
    }),
    
    // display auth view
    authLock = function()
    {
        var args = arguments,
            self = this;

        // reset headers on success
        AuthApp.success = function()
        { 
            //self.options.headers.Authorization = localStorage.getItem('superdesk.login.session');
        };
        AuthApp.require.apply(self, arguments); 
    },
    
    authSync = $.extend({}, newSync, 
    {
        options: 
        {
			
            // get login token from local storage
			//console.log('why');
            //headers: { 'Authorization': localStorage.getItem('superdesk.login.session') },
            // failuire function for non authenticated requests
            fail: function(resp)
            { 
                // TODO 404? shouldn't be covered by auth
                (resp.status == 401) && authLock.apply(authSync, arguments);
                (resp.status == 404) && ErrorApp.require.apply(this, arguments);
            } 
        },
        href: function(source)
        {
            return source.indexOf('my/') === -1 ? source.replace('resources/','resources/my/') : source;
        }
    }),
    xfilter = function() // x-filter implementation
    {
        if( !this.syncAdapter.options.headers ) this.syncAdapter.options.headers = {};
        this._xfilter = arguments.length > 1 ? $.makeArray(arguments).join(',') : $.isArray(arguments[0]) ? arguments[0].join(',') : arguments[0];
		this.syncAdapter.options.headers['X-Filter'] = this._xfilter;
		this.syncAdapter.options.headers['X-Format-DateTime'] = 'M/dd/yyyy HH:mm:ss';
        return this;
    },
    param = function(value, key)
	{
        if(value === undefined)
			delete this.syncAdapter.options.data[key];
		else {
			if(this.syncAdapter.options.data === undefined)
				this.syncAdapter.options.data = {};
			this.syncAdapter.options.data[key] = value;
		}
		return this;
	},
	since = function(value, key) // change id implementation
    {
		if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.since');
    },
	until = function(value, key) // change id implementation
    {
		if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.until');
    },	
	start = function(value, key) // change id implementation
    {
		if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.start');
    },	
	end = function(value, key) // change id implementation
    {
		if(key === undefined)
			key = 'CId';
		return param.call(this, value, key+'.end');
    },	

    asc = function(value)
    {
		return param.call(this, value, 'asc');
    },
    desc = function(value)
    {
		return param.call(this, value, 'desc');
    },
	limit = function(value)
	{
        return param.call(this, value, 'limit');
	},
	offset = function(value)
	{
		return param.call(this, value, 'offset');
	},
    Model = giz.Model.extend // superdesk Model 
    ({
        isDeleted: function(){ return this._forDelete || this.data.DeletedOn; },
        syncAdapter: newSync,
        xfilter: xfilter,
        since: since,
		until: until,
		start: start,
		end: end
    }),
    Auth = function(model)
    {
        if( typeof model === 'object' )
            model.syncAdapter = authSync; 
        model.modelDataBuild = function(model)
        {
            return Auth(model);
        };
        return model;
    },
    AuthModel = Model.extend // authenticated superdesk Model
    ({ 
        syncAdapter: authSync, xfilter: xfilter, since: since, until: until
    }),
    Collection = giz.Collection.extend
    ({
        xfilter: xfilter, since: since, until: until, start: start, end: end, asc: asc, desc: desc, limit: limit, offset: offset, syncAdapter: newSync
    }),
    AuthCollection = Collection.extend
    ({
        xfilter: xfilter, since: since, until: until, start: start, end: end, syncAdapter: authSync
    });
    
    // finally add unique container model
    Model.extend = function()
    {
        var Model = giz.Model.extend.apply(this, arguments);
        
        var uniq = new giz.UniqueContainer;
        $.extend( Model.prototype, 
        { 
            _uniq: uniq, 
            pushUnique: function()
            { 
                return uniq.set(this.hash(), this); 
            } 
        }, arguments[0] );
        return Model;
    };
    
    $.gizmo = { 
        Model: Model, AuthModel: AuthModel, 
        Collection: Collection, AuthCollection: AuthCollection, 
        Sync: newSync, AuthSync: authSync,
		View: giz.View,
		Url: giz.Url,
		Register: giz.Register		
    };
    self.preLoad(giveBack$);    
})(jQuery);
    
}

/*!
 * Returns true if the data object is compose of only given keys
 */
function isOnly(data, keys) 
{
	if ($.type(keys) === 'string')
		keys = [keys];
	var count = 0, checkCount = keys.length;		
	for(i in data) {
		if( -1 === $.inArray(i, keys))
			return false;
		count++;	
		if( count>checkCount ) return false;
	};
	return (count === checkCount);
}

var root = this;
window.livedesk.loadXDRequest = function (jQuery) {
    
    (function( jQuery ) {
        
    if (root.XDomainRequest) {
      jQuery.ajaxTransport("+*",function( s ) {
        if ( s.crossDomain && s.async ) {
          if ( s.timeout ) {
            s.xdrTimeout = s.timeout;
            delete s.timeout;
          }
          var xdr;
          return {
            send: function( _, complete ) {
              function callback( status, statusText, responses, responseHeaders ) {
                xdr.onload = xdr.onerror = xdr.ontimeout = jQuery.noop;
                xdr = undefined;
                complete( status, statusText, responses, responseHeaders );
              }
              xdr = new XDomainRequest();
              if(s.dataType){
                  var headerThroughUriParameters = "";//header_Accept=" + encodeURIComponent(s.dataType);
                  for(i in s.headers) {
                      headerThroughUriParameters += i +'='+encodeURIComponent(s.headers[i])+'&';
                  }
                  headerThroughUriParameters = headerThroughUriParameters.replace(/(\s+)?.$/, '');
                  s.url = s.url + (s.url.indexOf("?") === -1 ? "?" : "&" ) + headerThroughUriParameters;
              }
              xdr.open( s.type, s.url );
              xdr.onload = function(e1, e2) {
                callback( 200, "OK", { text: xdr.responseText }, "Content-Type: " + xdr.contentType );
              };
              xdr.onerror = function(e) {
                  //console.error(JSON.stringify(e));
                  callback( 404, "Not Found" );
              };
              if ( s.xdrTimeout ) {
                xdr.ontimeout = function() {
                  callback( 0, "timeout" );
                };
                xdr.timeout = s.xdrTimeout;
              }
              xdr.send( ( s.hasContent && s.data ) || null );
            },
            abort: function() {
              if ( xdr ) {
                xdr.onerror = jQuery.noop();
                xdr.abort();
              }
            }
          };
        }
      });
    }
    })( jQuery );

}

window.livedesk.init = function() {
	
	window.livedesk.location = window.location.href.split('#')[0];
	
    var self = this;
    var loadJQ = false;
    var giveBack$ = false;
    contentPath = self.contentPath === undefined? '': self.contentPath;
    
    if ((typeof jQuery == 'undefined') || 1) {
        loadJQ = true;
    } else {
        if(parseFloat($().jquery) < 1.7) {
            loadJQ = true;
            //relinquish control of $ variable
            giveBack$ = true;
        }
    }
    
    if (loadJQ) {
        self.loadScript('//ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js', function(){
            self.loadXDRequest(jQuery);
			if (typeof $.gizmo == 'undefined') {
                self.loadGizmo(giveBack$);
            } else {
                self.preLoad(giveBack$);
            }
        })
    } else {
		self.loadXDRequest(jQuery);
        if (typeof $.gizmo == 'undefined') {
            self.loadGizmo(giveBack$);
        } else {
            self.preLoad(giveBack$);
        }
    }
};
	
window.livedesk.loadScript = function (src, callback) {
		var script = document.createElement("script")
		script.type = "text/javascript";
		if (script.readyState) { //IE
			script.onreadystatechange = function () {
				if (script.readyState == "loaded" || script.readyState == "complete") {
					script.onreadystatechange = null;
					callback();
				}
			};
		} else { //Others
			script.onload = function () {
				callback();
			};
		}
		script.src = src;
		document.getElementsByTagName("head")[0].appendChild(script);
	};
window.livedesk.preLoad = function (giveBack$) {
    if (giveBack$) {
        var jq_17 = $.noConflict(true);
        this.startLoading(jq_17, window.livedesk._);
    } else {
        this.startLoading(jQuery, window.livedesk._);
    }
};

window.livedesk.startLoading = function($, _) {
		var 
		User = $.gizmo.Model.extend({}),
/*		PostType = $.gizmo.Model.extend({}),
		AuthorPerson = $.gizmo.Model.extend({}),
		PostBlog = $.gizmo.Model.extend({}),
		Author = $.gizmo.Model.extend({}),
*/		
		Post = $.gizmo.Model.extend
		({
			defaults:
			{
				Creator: User
			},
			services: {
				'flickr': true,
				'google': true,
				'twitter': true,
				'facebook': true,
				'youtube': true
			},
			/**
			* Get css class based on type
			*
			* @return {string}
			*/
			getClass: function() {
				switch (this.get('Type').Key) {
					case 'wrapup':
						return 'wrapup';
						break;

					case 'quote':
						return 'quotation';
						break;

					case 'advertisement':
						return 'advertisement';
						break;

					default:
						if (this.isService()) {
							return 'service';
						}

						return 'tw';
				}
			},
			/**
			* Test if post is from service
			*
			* @return {bool}
			*/
			isService: function() {
				return this.get('AuthorName') in this.services;
			},

			/**
			* Test if post is quote
			*
			* @return {bool}
			*/
			isQuote: function() {
				return this.getClass() == 'quotation';
			},
			twitter: {
				link: {
					anchor: function(str) 
					{
						return str.replace(/[A-Za-z]+:\/\/[A-Za-z0-9-_]+\.[A-Za-z0-9-_:%&\?\/.=]+/g, function(m) 
						{
							m = m.link(m);
							m = m.replace('href="','target="_blank" href="');
							return m;
						});
					},
					user: function(str) 
					{
						return str.replace(/[@]+[A-Za-z0-9-_]+/g, function(us) 
						{
							var username = us.replace("@","");
				
							us = us.link("http://twitter.com/"+username);
							us = us.replace('href="','target="_blank" onclick="loadProfile(\''+username+'\');return(false);"  href="');
							return us;
						});
					},
					tag: function(str) 
					{
						return str.replace(/[#]+[A-Za-z0-9-_]+/g, function(t) 
						{
							var tag = t.replace(" #"," %23");
							t = t.link("http://summize.com/search?q="+tag);
							t = t.replace('href="','target="_blank" href="');
							return t;
						});
					},
					all: function(str)
					{
						str = this.anchor(str);
						str = this.user(str);
						str = this.tag(str);
						return str;
					}
				}
			}
		}),
		AutoCollection = $.gizmo.Collection.extend
		({
			timeInterval: 10000,
			idInterval: 0,
			_latestCId: 0,
			/*!
			 * for auto refresh
			 */
			keep: false,
			init: function(){ 
				var self = this;
				this.on('readauto updatesauto read updates addings addingsauto',function(evt, data)
				{
					if(data === undefined)
						data = self._list;
					self.getMaximumCid(data);
				});
			},
			destroy: function(){ this.stop(); },
			auto: function(fn)
			{
				var self = this;
				ret = this.stop().start();
				this.idInterval = setInterval(function(){self.start();}, this.timeInterval);
				return ret;
			},
			getMaximumCid: function(data)
			{
				for(i=0, count=data.length; i<count; i++) {					
					var CId = parseInt(data[i].get('CId'))
					if( !isNaN(CId) && (this._latestCId < CId) )
						this._latestCId = CId;
				}
			},
			start: function()
			{
				var self = this, requestOptions = {data: {'cId.since': this._latestCId}, headers: { 'X-Filter': self._xfilter, 'X-Format-DateTime': 'M/dd/yyyy HH:mm:ss'}}; 
				if(self._latestCId === 0) delete requestOptions.data;
				if(!this.keep && self.view && !self.view.checkElement()) 
				{
					self.stop();
					return;
				}				
				this.triggerHandler('beforeUpdate');
				return this.autosync(requestOptions);
			},
			stop: function()
			{
				var self = this;
				clearInterval(self.idInterval);
				return this;
			},
			autosync: function()
			{
			var self = this;
			return (this.href &&
				this.syncAdapter.request.call(this.syncAdapter, this.href).read(arguments[0]).done(function(data)
				{
					var data = self._parse(data), addings = [], updates = [], count = self._list.length;
					 // important or it will infiloop
					for( var i=0; i < data.length; i++ )
					{
						var model = false;
						for( var j=0; j<count; j++ ) {
							if( data[i].hash() == self._list[j].hash() )
							{
								model = data[i];
								break;
							}
						}
						if( !model ) {
							if( !data[i].isDeleted() ) {
								self._list.push(data[i]);
								addings.push(data[i]);
							} else {
								updates.push(data[i]);						
							}
						}
						else {
							updates.push(model);
							if( model.isDeleted() ) {
								model._remove();
							} else {
								model.on('delete', function(){self.remove(this.hash());})
										.on('garbage', function(){this.desynced = true;});
							}
						}
					}
					self.desynced = false;
					/**
					 * If the initial data is empty then trigger READ event
					 * else UPDATE with the changeset if there are some
					 */
					if( ( count === 0) ){
						//console.log('read');
						self.triggerHandler('readauto');
					} else {                    
						/**
						 * Trigger handler with changeset extraparameter as a vector of vectors,
						 * caz jquery will send extraparameters as arguments when calling handler
						 */
						//console.log('update');
						self.triggerHandler('updatesauto', [updates]);
						self.triggerHandler('addingsauto', [addings]);
					}
				}));
			}
		
		});
        Posts = AutoCollection.extend({
			parse: function(data){
				if(data.total !== undefined) {
					data.total = parseInt(data.total);
					this.listTotal = data.total;
					delete data.total;
				}
				if(data.PostList)
					return data.PostList;
				return data;
			},
			model: Post
        }),
       
        Blog = $.gizmo.Model.extend
        ({
            defaults: 
            {
                //Post: Posts,
                PostPublished: Posts
                //PostUnpublished: Posts
            }
        });
        
        var i=0, LivedeskClass = {};
        LivedeskClass.PostItemView = $.gizmo.View.extend
        ({
            init: function()
            {
                        var self = this;
                        self.xfilter = 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta';
                        self.model
                                .on('read update', function(evt, data){
										//console.log('this.data: ',$.extend({},this.data), ' is only:' ,isOnly(this.data, ['CId','Order']));
										/*if(isOnly(this.data, ['CId','Order']) || isOnly(data, ['CId','Order'])) {
												console.log('this.data: ',$.extend({},this.data));
												console.log('data: ',$.extend({}, data));
												console.log('force');
												self.model.xfilter(self.xfilter).sync({force: true});
                                        }
                                        else*/
										{
                                            self.render(evt, data);
										}
                                })
                                .on('delete', self.remove, self)
                                .xfilter(self.xfilter)
                                .sync();
			},
			remove: function()
			{
				var self = this;
				self._parent.removeOne(self);
				self.el.remove();
				return self;			
			},
            itemTemplate: function(item, content, time, Avatar)
			{
				// Tw------------------------------------------------------------------------------------------------
				var returned = '';
                                var itemClass = item.getClass();
                                var author = item.get('AuthorName');
                                var annotBefore = '';
                                var annotAfter = '';
                                if (item.data.hasOwnProperty('Meta')) {
                                    var Meta = item.data.Meta;
                                    if ( typeof Meta == 'string') {
                                        Meta = JSON.parse(Meta);
                                    }
                                    if ( Meta.hasOwnProperty('annotation') ) {
                                        if( typeof Meta.annotation === 'string' ) {
											if((Meta.annotation === '<br>') || (Meta.annotation === '<br/>') || (Meta.annotation === '<br />'))
												Meta.annotation = '';										
                                            annotAfter = '<div class="editable annotation">' + Meta.annotation + '</div>';   
                                        } else {
                                            if( Meta.annotation[1] !== null) {
                                                if((Meta.annotation[0] === '<br>') || (Meta.annotation[0] === '<br/>')|| (Meta.annotation[0] === '<br />') )
													Meta.annotation[0] = '';
                                                if((Meta.annotation[1] === '<br>') || (Meta.annotation[1] === '<br/>') || (Meta.annotation[1] === '<br />'))
													Meta.annotation[1] = '';											
                                                annotBefore = '<div class="editable annotation">' + Meta.annotation[0] + '</div>';
                                                annotAfter = '<div class="editable annotation">' + Meta.annotation[1] + '</div>';
                                            } else {
                                                if((Meta.annotation[0] === '<br>') || (Meta.annotation[0] === '<br/>')|| (Meta.annotation[0] === '<br />') )
													Meta.annotation[0] = '';											
                                                annotAfter = '<div class="editable annotation">' + Meta.annotation[0] + '</div>';
                                            }											
                                        }
                                    }
                                }
								avatarString = '';
                                if(_('no_avatar') != 'true' && Avatar.length > 0 && author != 'twitter') {
                                    avatarString = '<figure><img src="' + Avatar + '" ></figure>';
                                }                                
                                switch (itemClass) {
                                    case 'tw':
                                    case 'service':
                                        returned += annotBefore;
										returned += avatarString;
                                        returned +=  '<div class="result-content">';
                                        if ( author == 'twitter') {
                                            returned += '<blockquote class="twitter-tweet"><p>' + content + '</p>&mdash; ' + Meta.from_user_name + ' (@' + Meta.from_user_name + ') <a href="https://twitter.com/' + Meta.from_user + '/status/' + Meta.id_str + '" data-datetime="'+Meta.created_at+'"></a></blockquote>';
                                            
                                            if ( !window.livedesk.loadedTweeterScript || 1) {
                                                window.livedesk.loadScript('//platform.twitter.com/widgets.js', function(){});
                                                window.livedesk.loadedTweeterScript = true;
                                            }
                                        } else if ( author == 'youtube') {
											
                                            returned +=     '<div class="result-text">' + content + '</div>';
                                            returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ';										
											returned +=     '<a class="author-name" href="http://youtube.com/'+Meta.uploader+'" target="_blank">'+Meta.uploader+'</a>';
										} else if ( author == 'google'){
											//titleNoFormatting
											returned +=     '<h3><a target="_blank" href="'+Meta.unescapedUrl+'">'+Meta.title+'</a></h3>'
											returned +=     '<div class="result-text">' + content + '</div>';
                                            //returned +=     '<p class="attributes"><i class="source-icon"><img src="http://g.etfv.co/'+Meta.url+'" style="max-width: 16px" border="0"></i><a class="author-name" href="'+Meta.url+'">'+Meta.visibleUrl+'</a>'
											returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ' + item.get('AuthorName');
										} else if (author == 'flickr') {
                                            returned +=     '<div class="result-text">' + content + '</div>';
                                            returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ' + item.get('AuthorName');										
										}
										else {
                                            returned +=     '<div class="result-text">' + content + '</div>';
                                            returned +=     '<p class="attributes"><i class="source-icon"></i> '+_('by')+' ' + item.get('AuthorName');
											returned +=         '<time>' + time + '</time>';
										}
                                        returned +=     '</p>';
                                        returned += '</div>';
                                        returned += annotAfter;
                                        
                                        break;
                                    case 'quotation':
                                        var adition, authorName = item.get('AuthorName'), auxDiv = content.split('<div><br><br></div>'), auxBr = content.split('<br><br><br>');
										if(auxDiv.length == 2) {
											content = auxDiv[0];
											adition = '<div class="quotation-author">'+auxDiv[1]+'</div>';
										} else if (auxBr.length == 2) {
											content = auxBr[0];
											adition = '<div class="quotation-author">'+auxBr[1]+'</div>';
										}
										//returned += avatarString;
										returned +=  '<div class="result-content">';
                                        returned +=     '<div class="result-text">' + content + '</div>';
										if(adition)
											returned += adition;
										else
											returned +=     '<div class="attributes">'+_('by')+' ' + authorName + '</div>';
                                        returned += '</div>';
                                        break;
                                    case 'wrapup':
                                        returned += '<span class="big-toggle"></span>';
                                        returned += '<h3>' + content + '</h3>';
                                        break;
                                    case 'advertisement':
                                        returned += content;
                                        
                                }
                               return returned;
			},
                        toggleWrap: function(e, forceToggle) {
							if (typeof forceToggle != 'boolean' ) {
                                forceToggle = false;
                            }
                            this._toggleWrap($(e).closest('li').first(), forceToggle);
                        },
                        _toggleWrap: function(item, forceToggle) {
                            if (typeof forceToggle != 'boolean' ) {
                                forceToggle = false;
                            }
                            if (item.hasClass('open')) {
                                var collapse = true;
                                if ( collapse ) {
                                    item.removeClass('open').addClass('closed');
                                    item.nextUntil('.wrapup').hide();
                                } else {
                                    //don't collapse wrap'
                                }
                            } else {
                                item.removeClass('closed').addClass('open');
                                item.nextUntil('.wrapup').show();
                            }
                        },
                        togglePermalink: function(e) {
                            this._togglePermalink($(e).next('input[data-type="permalink"]'));
                        },
                        _togglePermalink: function(item) {
                            if (item.css('visibility') == 'visible') {
                               item.css('visibility','hidden');
                            } else {
                               item.css('visibility', 'visible');
                            }
                        },
			render: function()
			{
			
				var self = this, order = parseFloat(self.model.get('Order')), Avatar='';
				if(this.model.get('AuthorPerson') && this.model.get('AuthorPerson').EMail) {
					Avatar = $.avatar.get(self.model.get('AuthorPerson').EMail);
				}
				if ( !isNaN(self.order) && (order != self.order)) {
					self.order = order;
					self._parent.reorderOne(self);
				}
				var content = self.model.get('Content');

				var style= '';                
				if (self.model.getClass() == 'wrapup') {
					style += 'open ';
				}
				if (self.model.isService()) {
					style += self.model.get('AuthorName');
                                        
					var meta = JSON.parse(self.model.get('Meta'));
					
					var publishedon = self.model.get('PublishedOn');
					var datan = new Date(publishedon);
					var time = datan.format('ddd mmm dd yyyy HH:MM:ss TT');
                                        
					if (self.model.get('AuthorName') == 'flickr') {
						var paddedContent = '<span>' + content + '</span>';
						var jqo = $(paddedContent);
						jqo.find('img').attr('src', jqo.find('a').attr('href'));
						content = jqo.html();
					} else if (self.model.get('AuthorName') == 'twitter') {
                                                Avatar = meta.profile_image_url;
						content = self.model.twitter.link.all(content);
					} else if (self.model.get('AuthorName') == 'google') {
                                            if (meta.tbUrl) {
                                                content += '<p><a href="' + meta.url + '"><img src="' + meta.tbUrl + '" height="' + meta.tbHeight + '" width="' + meta.tbWidth + '"></a></p>';
                                            }
                                        }
				}
                                                                                             
				var publishedon = self.model.get('PublishedOn');
				var datan = new Date(publishedon);
				var time = datan.format(_('ddd mmm dd yyyy HH:MM:ss TT'));
				if(_('show_current_date') === 'true')
				{
					var currentDate = new Date();
					if(currentDate.format('mm dd yyyy') == datan.format('mm dd yyyy'))
						time = datan.format(_('HH:MM:ss TT'));
				}
				var author = self.model.get('AuthorName');
				
				content = self.itemTemplate(self.model, content, time, Avatar);
                                
				/*var postId = self.model.get('Id');
				var blogTitle = self._parent.model.get('Title');
				blogTitle = blogTitle.replace(/ /g, '-');
				var hash = postId + '-' +  encodeURI (blogTitle);
				*/
				var hash = self.model.get('Order');
				var itemClass = self.model.getClass();
				var fullLink = window.livedesk.location + '#' + self._parent.hashIdentifier + hash;
				var permalink = '';
				if(itemClass !== 'advertisement' && itemClass !== 'wrapup')
					permalink = '<a rel="bookmark" href="#'+ self._parent.hashIdentifier + hash +'">#</a><input type="text" value="' + fullLink + '" style="visibility:hidden" data-type="permalink" />';						
				var template ='<li class="'+ style + itemClass +'"><a name="' + hash + '"></a>' + content + '&nbsp;'+ permalink +'</li>';
                                
				if ( typeof window.livedesk.productionServer != 'undefined' && typeof window.livedesk.frontendServer != 'undefined' ){
					re = new RegExp(window.livedesk.productionServer, "g");
					template = template.replace(re, window.livedesk.frontendServer );
				}

				self.setElement( template );
				self.model.triggerHandler('rendered');
				$(self.el).off('click.livedesk', '.big-toggle').on('click.livedesk', '.big-toggle', function(){
					self.toggleWrap(this, true);
				});
				$(self.el).off('click.livedesk', 'a[rel="bookmark"]').on('click.livedesk', 'a[rel="bookmark"]', function() {
					self.togglePermalink(this);
				});
				$(self.el).off('click.livedesk', 'input[data-type="permalink"]').on('focus.livedesk click.livedesk', 'input[data-type="permalink"]', function() {
					$(this).select();
				});
			}
		}),
		totalLoad = 0,
		LivedeskClass.TimelineView = $.gizmo.View.extend
		({
			limit: 25,
			offset: 0,
			hashIdentifier: 'livedeskitem=',
			el: '#livedesk-root',
			timeInterval: 10000,
			idInterval: 0,
			_latestCId: 0,
			events: {
				'#liveblog-more': { click: 'more'}
			},
			more: function(evt) {
				var self = this,
					delta = self.model.get('PostPublished').delta;
					postPublished = self.model.get('PostPublished')
				if(self.filters) {
					$.each(self.filters, function(method, args) {
						postPublished[method].apply(postPublished, args);
					});
				}
				postPublished
					.xfilter(self.xfilter)
					.limit(self.limit)
					.offset(self._views.length)
					.sync().done(function(data){				
						var total = self.model.get('PostPublished').total;
						if(self._views.length >= total)
							$(evt.target).hide();
					});
			},
			setIdInterval: function(fn){
				this.idInterval = setInterval(fn, this.timeInterval);
				return this;
			},
			pause: function(){
				var self = this;
				clearInterval(self.idInterval);
				return this;
			},
			sync: function(){
				var self = this;
				this.auto().pause().setIdInterval(function(){self.auto();});
			},			
			auto: function(){
				this.model.xfilter().sync({force: true});
				return this;
			},
			ensureStatus: function(){
				if(this.model.get('ClosedOn')) {
					var closedOn = new Date(this.model.get('ClosedOn'));
					this.pause();
					this.model.get('PostPublished').pause();					
					this.el.find('#liveblog-status').html(_('The liveblog coverage was stopped ')+closedOn.format(_('mm/dd/yyyy HH:MM:ss')));
				}
			},                       
			gotoHash : function() {
				if (location.hash.length > 0) {
					var topHash = location.hash;
					location.hash = '';
					location.hash = topHash;
				}
			},
			init: function()
			{		
				var self = this;
				self._views = [];
				self.rendered = false;
				if($.type(self.url) === 'string')
					self.model = new Blog(self.url.replace('my/',''));				
				self.xfilter = 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta';
				//self.xfilter = 'CId';								   
				self.model.on('read', function()
				{
					//console.log('read');
					if(!self.rendered) {
						var hashIndex, 
							orderhash = window.location.href.split('#'),
							postPublished = self.model.get('PostPublished')
								.on('read readauto', self.render, self)
								.on('addings addingsauto', self.addAll, self)
								.on('addingsauto', self.updateTotal, self)
								.on('updates updatesauto', self.updateStatus, self)
								.on('beforeUpdate', self.updateingStatus, self)
								.xfilter(self.xfilter)
								.limit(self.limit);
						if(orderhash[1] && ( (hashIndex = orderhash[1].indexOf(self.hashIdentifier)) !== -1)) {
							var order = parseFloat(orderhash[1].substr(hashIndex+self.hashIdentifier.length));
							self.filters = {end: [order, 'order']};
							postPublished
								.one('rendered', self.showLiner, self)
								.end(order, 'order')
								.sync();
						} else {
								postPublished
									.offset(self.offset).auto();
						}
					}
					self.rendered = true;
				}).on('update', function(e, data){
					self.ensureStatus();
					self.renderBlog();
				});
				self.sync();				
			},
			showLiner: function()
			{
				var self = this;
				$('#liveblog-firstmore')
					.on('click', function(){
						self.el.find('#liveblog-post-list').html('');
						for(i=0, count = self._views.length; i<count; i++) {
							self._views[i].rendered = false;
						}
						self._views = [];
						delete self.filters;
						var postPublished = self.model.get('PostPublished');
						postPublished._list = [];						
						postPublished._latestCId = 0;
						postPublished
							.limit(self.limit)
							.offset(self.offset).auto();
						$(this).hide();
					})
					.show();
			},
			removeOne: function(view)
			{
				var 
					self = this,
					pos = self._views.indexOf(view);
				//console.log(self.model.get('PostPublished').total);
				self.model.get('PostPublished').total--;					
				self._views.splice(pos,1);
				return self;
			},
			reorderOne: function(view) {
				var self = this;
				self._views.sort(function(a,b){
					return a.order - b.order;
				});
				pos = self._views.indexOf(view);
				//console.log(pos, '===',(self._views.length-1));
				if(pos === 0) {
					//console.log(view.model.get('Content'), '.insertAfter('+self._views[1].model.get('Content')+');');
					view.el.insertAfter(self._views[1].el);
				} else {
					//console.log(view.model.get('Content'), '.insertBefore('+self._views[pos>0? pos-1: 1].model.get('Content')+');');
					view.el.insertBefore(self._views[pos>0? pos-1: 1].el);
				}
			},
			addOne: function(model)
			{
				var self = this,
					current = new LivedeskClass.PostItemView({model: model, _parent: self}),				    
					count = self._views.length;
				model.postview = current;
				current.order =  parseFloat(model.get('Order'));
				if(!count) {
					this.el.find('#liveblog-post-list').prepend(current.el);
					self._views = [current];
				} else {
					var next, prev;
					for(i=0; i<count; i++) {
						if(current.order>self._views[i].order) {
							next = self._views[i];
							nextIndex = i;
						} else if(current.order<self._views[i].order) {
							prev = self._views[i];
							prevIndex = i;
							break;
						}						
					}
					//console.log(prev && prev.order,'<<',current.order, '>>',next && next.order);
					if(prev) {
						//console.log('next');
						current.el.insertAfter(prev.el);
						self._views.splice(prevIndex, 0, current);					
					} else if(next) {
						//console.log('prev');
						current.el.insertBefore(next.el);
						self._views.splice(nextIndex+1, 0, current);
					}
				}
				return current;
			},
			updateTotal: function(evt,data)
			{
				var i = data.length;
				while(i--) {
						this.model.get('PostPublished').total++;
				}
				//console.log('total: ',this.model.get('PostPublished').total);
			},
			addAll: function(evt, data)
			{
				var i = data.length;
				while(i--) {
					this.addOne(data[i]);
				}
				this.toggleMoreVisibility();
			},
			updateingStatus: function()
			{
				this.el.find('#liveblog-status').html(_('updating...'));
			},
			updateStatus: function()
			{
				var now = new Date();
				this.el.find('#liveblog-status').fadeOut(function(){
					$(this).text(_('updated on ')+now.format(_('HH:MM:ss'))).fadeIn();
				});
			},
			renderBlog: function()
			{
				//$(this.el).find('article')
					//.find('h2').html(this.model.get('Title')).end()
					//.find('p').html(this.model.get('Description'));
			},
			toggleMoreVisibility: function()
			{				
				if(this.limit >= this.model.get('PostPublished').total ) {
					$('#liveblog-more',this.el).hide();
				} else {
					$('#liveblog-more',this.el).show();
				}			
			},
			render: function(evt)
			{				
				this.el.html('<article><h2></h2><p></p></article><div class="live-blog"><p class="update-time" id="liveblog-status"></p><div class="liveblog-more-container"><a class="liveblog-more" id="liveblog-firstmore" href="javascript:void(0)" style="display:none !important;">'+_('Load more posts')+'</a></div><div id="liveblog-posts"><ol id="liveblog-post-list" class="liveblog-post-list"></ol></div><div><a id="liveblog-more" class="liveblog-more" href="javascript:void(0)">'+_('More')+'</a></div>');
				this.renderBlog();
				this.ensureStatus();
				var postPublished = this.model.get('PostPublished');
				data = postPublished._list;
				postPublished.total = postPublished.listTotal;
				this.toggleMoreVisibility();
				var next = this._latest, current, model, i = data.length;                               
				totalLoad = data.length;
				var self = this, auxView;
				this.views=[];
				this.renderedTotal = i;
				while(i--) {
					data[i].on('rendered', this.renderedOn, this);
					auxView = this.addOne(data[i]);
					this.views.push(auxView);
				}
                this.model.get('PostPublished').triggerHandler('rendered');           
			},
			renderedOn: function(){
			   this.renderedTotal--;
			   if(!this.renderedTotal) {
					this.closeAllButFirstWrapup();
			   }
			},
			closeAllButFirstWrapup: function(views) {
				var first = true, views= this.views;
				views.reverse();
				for (var i = 0; i < views.length; i++) {
					 if ($(views[i].el).hasClass('wrapup')) {
						  views[i]._toggleWrap($(views[i].el));
					 }
				}
			}
		});
		window.livedesk.TimelineView = LivedeskClass.TimelineView;
		window.livedesk.callback();
	};
window.livedesk.init();