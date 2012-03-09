$(function()
{
	$('#area-main').html(layout);
	
	// main application, on deferred success
	var app = function(URL) 
	{
		/*!
		 * Display the request list
		 */
		var displayPattern = function()
			{
				// desired request index
				if(typeof arguments[0] == 'string')
					var index = {Id: arguments[0]};
				else
					var index = {Id: $(this).find('a[request-id]').attr('request-id')};
	
				requests.from(index)
					.xfilter('Get.*, Update.*, Delete.*, Insert.*')
					.spawn()
				.done(function( request, requestResource )
				{
					$('#area-content', layout)
						.tmpl( $('#request-descr-tmpl', superdesk.tmplRepo), {Request: request} ); // need object for iteration
					// attach spawned resource to the info button
					$('header', '#area-content')
						.prop('api-resource', requestResource)
						.eq(0).trigger('click');
				});
				return false;
			},
			/*!
			 * Display methods available for a request pattern
			 */
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
			},
			// the requests' resource
			requests = new $.rest(URL+'Request').xfilter('Pattern, Id'),
			// the inputs available on the API
			inputRequests = new $.rest(URL+'Input').xfilter('ForRequest.Pattern, ForRequest.Id');

		// bind click on header to open method description box
		$(document).off('click.superdesk', '#area-content article header');
		$(document).on('click.superdesk', '#area-content article header', displayMethod);
		
		// generate list of available requests
		requests.done(function(requestList)
		{
			$('#area-sidebar-left', layout)
				.tmpl($('#request-list-tmpl', superdesk.tmplRepo), {request: requestList})
				.find('ul').children().off('click').on('click', displayPattern);
		}, appFail);
		
		// handle search
		$('input.search-query').parents('form:eq(0)').on('submit', function()
		{
			var searchWord = $(this).find('input.search-query').val().toLowerCase(),
				results = [];
			
			if(searchWord == '') return false;
			
			inputRequests.done(function(data)
			{
				for(var i in data)
					if(data[i].ForRequest.Pattern.toLowerCase().indexOf(searchWord) != -1)
						results.push(data[i]);
	
				var firstOne;
				for(var i in results) 
				{
					$('#request-list a[request-id="'+results[i].ForRequest.Id+'"]').parent()
						.one('click', function(){ $(this).removeClass('hilite'); })
						.addClass('hilite');
					if(typeof firstOne == 'undefined') 
					{
						displayPattern(results[i].ForRequest.Id);
						firstOne = true;
					}
				}
			});
			return false;
		});
	},
	appFail = function()
	{
		$('#area-error').html('').tmpl($('#request-fail-tmpl', superdesk.tmplRepo));
	};
	
	superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/request/request.html')
		.done(function(){ app(superdesk.apiUrl+'/resources/Devel/'); });
});

