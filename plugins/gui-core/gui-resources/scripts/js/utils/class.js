define('utils/class', function() {
	var initializing = false;
	// The base Class implementation (does nothing)
	var Class = function(){};

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
				try { 
					var constructor = this._construct || this._constructor; 
					return constructor.apply(this, arguments);
				}
				catch(e) {
					console.error(e);
				}
		}

		// Populate our constructed prototype object
		Class.prototype = prototype;

		// Enforce the constructor to be what we expect
		Class.prototype.constructor = Class;

		// And make this class extendable
		Class.extend = arguments.callee;

		return Class;
	};
	return Class;
});