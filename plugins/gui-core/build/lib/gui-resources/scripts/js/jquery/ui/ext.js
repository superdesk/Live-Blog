/*!
 * jQuery UI Widget Override
 * addon to jQuery UI 1.8.16 
 */
// TODO move into some general js lib
define('jqueryui/ext',['jquery', 'jqueryui/widget', 'jqueryui/dialog'], function($) {
	Function.prototype.inherits = function( parentClassOrObject )
	{ 
		if( parentClassOrObject.constructor == Function ) //Normal Inheritance 
		{ 
			this.prototype = new parentClassOrObject;
			this.prototype.constructor = this;
			this.prototype.parent = parentClassOrObject.prototype;
			this.prototype.parentClass = parentClassOrObject;
		} 
		else //Pure Virtual Inheritance 
		{ 
			this.prototype = parentClassOrObject;
			this.prototype.constructor = this;
			this.prototype.parent = parentClassOrObject;
		} 
		return this;
	};
	(function( $, undefined ) 
	{
		$.widget.bridge = function( name, object ) 
		{
			// prepare plugins for 'per-selector' instances
            var pluginsClass = function(){};
			if( typeof object.prototype.plugins !== 'undefined' )
			{
				for( var i in object.prototype.plugins )
					pluginsClass.prototype[i] = object.prototype.plugins[i];
			}
			var prototypeOptions = object.prototype.options;
			
			$.fn[ name ] = function( options ) 
			{ 
				var isMethodCall = typeof options === "string",
					args = Array.prototype.slice.call( arguments, 1 ),
					returnValue = this;

				options = !isMethodCall && args.length ?
					$.extend.apply( null, [ true, options ].concat(args) ) :
					options;

				if( isMethodCall && options.charAt( 0 ) === "_" ) 
					return returnValue;

				var applyPlugins = function(self, applyPlugins)
				{
					var objectModel = new object;
					objectModel.plugins = new pluginsClass;
					
					if( !applyPlugins) 
						extendPlugins = options && options.plugins ? options.plugins : {};	
					else 
						extendPlugins = applyPlugins;

					// extend with user plugins from options
					objectModel.plugins = $.extend( objectModel.plugins, extendPlugins);
					objectModel.options = $.extend( true, {}, objectModel._getCreateOptions(), prototypeOptions, options);
					var extendPlugins = (applyPlugins ? applyPlugins : objectModel.plugins);
					if( typeof objectModel.plugins != 'undefined' )
						for( var i in extendPlugins ) 
						{
							if( $.isFunction(extendPlugins[i]) ) // instantiate if function
								objectModel.plugins[i] = new extendPlugins[i];
							if( objectModel.plugins[i] && $.isFunction(objectModel.plugins[i]._create) ) // call init per plugin
								objectModel.plugins[i]._create.call(objectModel, self);
						}
					
					if(objectModel.pluginsDestroy) self.on('remove', function()
	                { 
	                    objectModel.pluginsDestroy.call(objectModel, self); 
	                });
				};
				
				if( isMethodCall )
				{
					if( options == 'plugin' ) // TODO needs some rethinking
						applyPlugins(this, args[0]);
					
					this.each(function() 
					{
						var instance = $.data( this, name ),
							methodValue = instance && $.isFunction( instance[options] ) ?
								instance[ options ].apply( instance, args ) :
								instance;
						if ( methodValue !== instance && methodValue !== undefined ) 
						{
							returnValue = methodValue;
							return false;
						}
					});
				}
				else 
				{
					applyPlugins(this);
					this.each(function() 
					{
						var instance = $.data( this, name );
						if( instance ) 
							instance.option( options || {} )._init();
						else 
							$.data( this, name, new object( options, this ) );
					});
				}
				
				return returnValue;
			};
		};
	})( $ );
});