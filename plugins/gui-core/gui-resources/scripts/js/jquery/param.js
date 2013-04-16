define('jquery/param',['jquery'], function($) {

	function buildParams( prefix, obj, traditional, add ) {
		if ( jQuery.isArray( obj ) ) {
			// Serialize array item.
			jQuery.each( obj, function( i, v ) {
				if ( traditional || rbracket.test( prefix ) ) {
					// Treat each array item as a scalar.
					add( prefix, v );

				} else {
					// If array item is non-scalar (array or object), encode its
					// numeric index to resolve deserialization ambiguity issues.
					// Note that rack (as of 1.0.0) can't currently deserialize
					// nested arrays properly, and attempting to do so may cause
					// a server error. Possible fixes are to modify rack's
					// deserialization algorithm or to provide an option or flag
					// to force array serialization to be shallow.
					buildParams( prefix + "[" + ( typeof v === "object" ? i : "" ) + "]", v, traditional, add );
				}
			});

		} else if ( !traditional && jQuery.type( obj ) === "object" ) {
			// Serialize object item.
			for ( var name in obj ) {
				buildParams( prefix + "[" + name + "]", obj[ name ], traditional, add );
			}

		} else {
			// Serialize scalar item.
			add( prefix, obj );
		}
	}
	var r20 = /%20/g,
		rbracket = /\[\]$/,
		rCRLF = /\r?\n/g,
		rinput = /^(?:color|date|datetime|datetime-local|email|hidden|month|number|password|range|search|tel|text|time|url|week)$/i,
		rselectTextarea = /^(?:select|textarea)/i;
	$.extend
	({
		param: function( a, traditional ) {
			var s = [],
				add = function( key, value ) {
					var index = s.length;
					// If value is a function, invoke it and return its value
					value = jQuery.isFunction( value ) ? value() : value;
					s[ index ] = encodeURIComponent( key );
					if(value !== null)
						s[ index ] += "=" + encodeURIComponent( value );
				};

			// Set traditional to true for jQuery <= 1.3.2 behavior.
			if ( traditional === undefined ) {
				traditional = jQuery.ajaxSettings.traditional;
			}

			// If an array was passed in, assume that it is an array of form elements.
			if ( jQuery.isArray( a ) || ( a.jquery && !jQuery.isPlainObject( a ) ) ) {
				// Serialize the form elements
				jQuery.each( a, function() {
					add( this.name, this.value );
				});

			} else {
				// If traditional, encode the "old" way (the way 1.3.2 or older
				// did it), otherwise encode params recursively.
				for ( var prefix in a ) {
					buildParams( prefix, a[ prefix ], traditional, add );
				}
			}

			// Return the resulting serialization
			return s.join( "&" ).replace( r20, "+" );
		}
	});
});