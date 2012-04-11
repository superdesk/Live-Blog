define([
    'jquery','jquery.superdesk','jquery.tmpl','jquery.rest',
    'tmpl!layouts/list',
    'tmpl!request>list',
], function($, superdesk)
{ 
    URL = superdesk.apiUrl+'/resources/Devel/';
	var requests = new $.rest(URL+'Request').xfilter('Pattern, Id'),
	/*!
	 * Display methods available for a request pattern
	 */
	displayPattern = function()
		{
			// desired request index
			if(typeof arguments[0] == 'string')
				var index = {Id: arguments[0]};
			else
				var index = {Id: $(this).find('a[request-id]').attr('request-id')};
			
			console.log(index);
			requests.from(index)
				.get('Get')
				.get('Update')
				.get('Delete')
				.get('Insert')					
				//.xfilter('Get.*, Update.*, Delete.*, Insert.*')
				.spawn()
			.done(function( request, requestResource )
			{
				console.log(arguments);
/*					$('#area-content', '#area-main')
						.tmpl( 'description', {Request: request} ); // need object for iteration
					// attach spawned resource to the info button
					$('header', '#area-content')
						.prop('api-resource', requestResource)
						.eq(0).trigger('click');
*/						
			});
			return false;
		},		 
	displayMethod = function()
		{
			var displayBox = $(this).nextAll('.box');
			if( displayBox.is(':visible') )
			{
				displayBox.slideUp('fast');
				return false;	
			}
			
			var apiMethod = $(this).find('a').attr('api-method'),
				tmpl;
			switch(apiMethod.toLowerCase())
			{
				case 'get':
				case 'insert':
				case 'update':
				case 'delete':
					tmplName = '#request-method-tmpl';
					break;
				case 'input':
				case 'develinput':
					tmplName = '#request-inputlist-tmpl';
					break;
				default:
					console.error(apiMethod);
			}
			
			$(this).prop('api-resource')
			// or like this: var methodResource = new $.rest($(this).attr('href'));
			.get(apiMethod)
			.done(function(methodData)
			{
				$.tmplOption({varname: 'input'});
				displayBox.tmpl($(tmplName, superdesk.tmplRepo), methodData).slideDown('fast');
			});
			return false;
		};		
	// the inputs available on the API
	//$(document).off('click.superdesk', '#area-content article header');
	//$(document).on('click.superdesk', '#area-content article header', displayMethod);
	
	// generate list of available requests
	requests.done(function(request)
	{
		$('#area-main').tmpl('layouts/list', {request: request})
		.find('ul').children().off('click').on('click', displayPattern);
	});
});

