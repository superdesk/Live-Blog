define([
    'jquery','jquery/superdesk','jquery/tmpl','jquery/rest', 
    'tmpl!layouts/list',
    'tmpl!request>list',
], function($, superdesk)
{ 
    var ListApp = function()
    {
        URL = 'Devel/';
        
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
    			
    			requests.from(index).xfilter('Get.*, Update.*, Delete.*, Insert.*')
    				/*.get('Get').get('Update').get('Delete').get('Insert')*/					
    				.spawn()
    			.done(function( request, requestResource )
    			{
    			    require(['tmpl!request>method', 'tmpl!request>description'], function()
    			    {
        			    var content = $('[is-content]', '#area-main')
        						.tmpl( 'request>description', {Request: request} ); // need object for iteration
        					// attach spawned resource to the info button
        			    $('header', content)
        					.prop('api-resource', requestResource)
        					.eq(0).trigger('click');
    			    });
    			});
    			return false;
    		},		 
    		
    		displayMethod = function(evt)
    		{
    			var displayBox = $(this).nextAll('.box');
    			if( displayBox.is(':visible') )
    			{
    				displayBox.slideUp('fast');
    				return false;	
    			}
    			var apiMethod = $(this).find('a').attr('api-method'), self = this, tmpl;
    			switch(apiMethod.toLowerCase())
    			{
    				case 'get':
    				case 'insert':
    				case 'update':
    				case 'delete':
    				    displayBox.slideDown('fast');
    					break;
    				case 'input':
    				case 'develinput':
    				    require(['tmpl!request>inputlist'], function()
    				    {
    				        $(self).prop('api-resource').get(apiMethod).done(function(inputList)
    			            {
    				            displayBox.tmpl('request>inputlist', inputList).slideDown('fast');
    			            });
    				    });
    					break;
    				default:
    					console.error(apiMethod);
    			}
    			evt.preventDefault();
    		};		
    		
    	// the inputs available on the API
    	$(document)
    	    .off('click.superdesk', '[is-content] article header')
    	    .on('click.superdesk', '[is-content] article header', displayMethod);
    	
    	// generate list of available requests
    	requests.done(function(request)
    	{
    		$('#area-main').tmpl('request>list', {request: request, ui:{ content: 'is-content=1'}})
    		    .find('ul').children()
    		        .off('click.superdesk').on('click.superdesk', displayPattern);
    	});
    };
    return ListApp;
});

