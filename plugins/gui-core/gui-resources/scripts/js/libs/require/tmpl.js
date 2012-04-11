// Define the TEMPLATE PLUG-IN.
define(
	function(){
 
 
		// I load the given resource.
		var loadResource = function(
			resourceName,
			parentRequire,
			callback,
			config
			){
 
			// Parse the resource - extract the path to the template
			// file and the class name of the script.
			var resourceConfig = parseResource( resourceName );
 
			// Get the path to the template file.
			var resourcePath = resourceConfig.resourcePath;
 
			// Get the class name of the script tag (with our markup).
			var templateClass = resourceConfig.templateClass;
 
 
			// Load the template class.
			parentRequire(
				[
					("text!" + resourcePath)
				],
				function( templateContent ){
 
					// Wrap the template content in a DIV tag just
					// to make sure we have a parent element.
					templateContent = (
						"<div>" + templateContent + "</div>"
					);
 
					// Create the templates node.
					var templates = $( templateContent );
 
					// Get the template that was requrested by the
					// class name.
					var targetTemplate = templates.find( "script." + templateClass );
 
					// Create a jQuery DOM element out of the
					// template markup and pass it back to the
					// loader.
					callback(
						$( targetTemplate.html() )
					);
 
				}
			);
 
		};
 
 
		// When the resource name is passed to this plugin, it is in
		// the form of:
		//
		// resourcePath:className
		//
		// ... where resourcePath is the path to the HTML file that
		// contains our templates and className is the class attribute
		// of the Script tag that contains our template markup.
		var parseResource = function( resourceName ){
 
			// Split the resource into parts.
			var resourceParts = resourceName.split( ":" );
 
			// Get the resource path to our HTML file.
			var resourcePath = resourceParts[ 0 ];
 
			// Get the class name of our template markup container.
			var templateClass = resourceParts[ 1 ];
 
			// Return the resource configuration.
			return({
				resourcePath: resourcePath,
				templateClass: templateClass
			});
 
		};
 
 
		// --------------------------------------------------- //
		// --------------------------------------------------- //
 
 
		// Return the public API for the plugin. The only required
		// function in the plugin API is the load() function.
		return({
			load: loadResource
		});
 
 
	}
);