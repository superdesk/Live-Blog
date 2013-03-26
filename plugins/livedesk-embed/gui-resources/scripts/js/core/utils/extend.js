define(function(){
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