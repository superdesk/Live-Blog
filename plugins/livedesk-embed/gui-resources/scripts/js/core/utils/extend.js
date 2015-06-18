define(function(){
	if (!Array.prototype.indexOf) {
	  Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {
	    "use strict";
	    if (this == null) {
	      throw new TypeError();
	    }
	    var t = Object(this);
	    var len = t.length >>> 0;

	    if (len === 0) {
	      return -1;
	    }
	    var n = 0;
	    if (arguments.length > 1) {
	      n = Number(arguments[1]);
	      if (n != n) { // shortcut for verifying if it's NaN
	        n = 0;
	      } else if (n != 0 && n != Infinity && n != -Infinity) {
	        n = (n > 0 || -1) * Math.floor(Math.abs(n));
	      }
	    }
	    if (n >= len) {
	      return -1;
	    }
	    var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
	    for (; k < len; k++) {
	      if (k in t && t[k] === searchElement) {
	        return k;
	      }
	    }
	    return -1;
	  }
	}
	if (!Object.keys) {
	  Object.keys = (function () {
	    var hasOwnProperty = Object.prototype.hasOwnProperty,
	        hasDontEnumBug = !({toString: null}).propertyIsEnumerable('toString'),
	        dontEnums = [
	          'toString',
	          'toLocaleString',
	          'valueOf',
	          'hasOwnProperty',
	          'isPrototypeOf',
	          'propertyIsEnumerable',
	          'constructor'
	        ],
	        dontEnumsLength = dontEnums.length;

	    return function (obj) {
	      if (typeof obj !== 'object' && typeof obj !== 'function' || obj === null) throw new TypeError('Object.keys called on non-object');

	      var result = [];

	      for (var prop in obj) {
	        if (hasOwnProperty.call(obj, prop)) result.push(prop);
	      }

	      if (hasDontEnumBug) {
	        for (var i=0; i < dontEnumsLength; i++) {
	          if (hasOwnProperty.call(obj, dontEnums[i])) result.push(dontEnums[i]);
	        }
	      }
	      return result;
	    };
	  })();
	}
	
	if ( !Array.prototype.forEach ) {
	  Array.prototype.forEach = function(fn, scope) {
		for(var i = 0, len = this.length; i < len; ++i) {
		  fn.call(scope || this, this[i], i, this);
		}
	  }
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
	/**
	 * Date.parse with progressive enhancement for ISO 8601 <https://github.com/csnover/js-iso8601>
	 * © 2011 Colin Snover <http://zetafleet.com>
	 * Released under MIT license.
	 */
	(function (Date, undefined) {
		var origParse = Date.parse, numericKeys = [ 1, 4, 5, 6, 7, 10, 11 ];
		Date.parse = function (date) {
			var timestamp, struct, minutesOffset = 0;

			// ES5 §15.9.4.2 states that the string should attempt to be parsed as a Date Time String Format string
			// before falling back to any implementation-specific date parsing, so that’s what we do, even if native
			// implementations could be faster
			//              1 YYYY                2 MM       3 DD           4 HH    5 mm       6 ss        7 msec        8 Z 9 ±    10 tzHH    11 tzmm
			if ((struct = /^(\d{4}|[+\-]\d{6})(?:-(\d{2})(?:-(\d{2}))?)?(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{3}))?)?(?:(Z)|([+\-])(\d{2})(?::(\d{2}))?)?)?$/.exec(date))) {
				// avoid NaN timestamps caused by “undefined” values being passed to Date.UTC
				for (var i = 0, k; (k = numericKeys[i]); ++i) {
					struct[k] = +struct[k] || 0;
				}

				// allow undefined days and months
				struct[2] = (+struct[2] || 1) - 1;
				struct[3] = +struct[3] || 1;

				if (struct[8] !== 'Z' && struct[9] !== undefined) {
					minutesOffset = struct[10] * 60 + struct[11];

					if (struct[9] === '+') {
						minutesOffset = 0 - minutesOffset;
					}
				}

				timestamp = Date.UTC(struct[1], struct[2], struct[3], struct[4], struct[5] + minutesOffset, struct[6], struct[7]);
			}
			else {
				timestamp = origParse ? origParse(date) : NaN;
			}

			return timestamp;
		};
	}(Date));
	if ( !Date.prototype.toISOString ) {
		 
		( function() {
		 
			function pad(number) {
				var r = String(number);
				if ( r.length === 1 ) {
					r = '0' + r;
				}
				return r;
			}
	  
			Date.prototype.toISOString = function() {
				return this.getUTCFullYear()
					+ '-' + pad( this.getUTCMonth() + 1 )
					+ '-' + pad( this.getUTCDate() )
					+ 'T' + pad( this.getUTCHours() )
					+ ':' + pad( this.getUTCMinutes() )
					+ ':' + pad( this.getUTCSeconds() )
					+ '.' + String( (this.getUTCMilliseconds()/1000).toFixed(3) ).slice( 2, 5 )
					+ 'Z';
			};
	   
		}() );
	}       
	//addition to make smart wrap not a default method
	String.prototype.trunc =
	function(n,useWordBoundary){
		var toLong = this.length>n,
			s_ = toLong ? this.substr(0,n-1) : this;
		s_ = useWordBoundary && toLong ? s_.substr(0,s_.lastIndexOf(' ')) : s_;
		return  toLong ? s_ + '...' : s_;
	 };
});