$.extend( $, 
{
	/*!
	 * Loads template files via ajax and extracts the templates
	 * 
	 * @param string path 
	 * 	the url from which to load templates
	 * @param string selector 
	 * 	optional, selector to use to match templates in loaded file
	 * @returns $.Deferred
	 */
	getTmpl: function(path)
	{
		var tplSelector = typeof arguments[1] != 'undefined' ? arguments[2] : "script[type='text/x-jQuery-tmpl']", 
			dfd = new $.Deferred;
		$.ajax(path, {dataType: 'html'}).done(function(html)
		{ 
			var templates = [];
			$(html).each(function(i, elem){ if($(elem).is(tplSelector)) templates.push(elem); });
			
		// ----------------?--------------- //
			$('head').append(templates);
		// ----------------?--------------- //
			
			dfd.resolve(templates);
		})
		return dfd;
	}
});
var superdesk = 
{
	layouts: {},
	/*!
	 * load layout to superdesk object layouts
	 * @param string path layout path
	 * @param string name layout name
	 */
	loadLayout: function(path, name)
	{
		return $.ajax( superdesk.apiUrl+path, {dataType: 'html'})
			.done(function(data)
			{
				// need to wrap it in a <div /> tag for $ selector to work
				var layoutObject = $('<div>'+data+'</div>');
				if( typeof name == 'string')
					superdesk.layouts[name] = layoutObject;
				else
					name = layoutObject;
				
				return layoutObject;
			});
	},
	/*!
	 * Loads and applies script to a layout object
	 * 
	 * @param string scriptPath 
	 * @param object layoutObject 
	 * @param bool fullPath if true superdesk.apiUrl will not be included
	 */
	applyScriptToLayout: function(scriptPath, layoutObject, fullPath)
	{
		return $.ajax((!fullPath ? superdesk.apiUrl : '') + '/' + scriptPath, {dataType: 'text'})
			.done(function(data)
			{
				// TODO additional security checking here
				(new Function('layout', data)).call(null, layoutObject);
			});
	}
};
