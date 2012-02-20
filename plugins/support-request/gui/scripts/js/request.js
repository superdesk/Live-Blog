// main application, on deferred success
var app = function(URL) 
{
	$('#alert-box').html('');
	$('#menu-api-url').text(URL).attr('href', URL);
	
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
				$('#request-descr').tmpl( '#request-descr-tmpl', {Request: request} ); // need object for iteration
				// attach spawned resource to the info button
				$('header', '#request-descr')
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
					tmpl = '#request-method-tmpl';
					break;
				case 'develinput':
					tmpl = '#request-inputlist-tmpl';
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
				var html = $.tmpl(tmpl, methodData);
				
				displayBox.html(html || '<em>nothing here</em>').slideDown('fast');
			});
			return false;
		},
		
		// the requests' resource
		requests = new $.rest(URL+'Request').xfilter('Pattern, Id'),
		
		// the inputs available on the API
		inputRequests = new $.rest(URL+'Input').xfilter('ForRequest.Pattern, ForRequest.Id');
		
	// bind click on header to open method description box
	$(document).off('click', '#request-descr article header');
	$(document).on('click', '#request-descr article header', displayMethod);
	
	// generate list of available requests
	requests.done(function(requestList)
	{
		document.cookie = 'api-url='+URL+'; expires='+
			(function(){var d = new Date(); d.setDate(d.getDate() + 7); return d.toUTCString(); })();
		
		$('#request-list').tmpl( '#request-list-tmpl', {request: requestList} )
		.children().off('click').on('click', displayPattern);
		
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
	})
	
},

appFail = function()
{
	$($.tmpl('#request-fail-tmpl', {})).appendTo($('#alert-box').html(''));
};

$(function()
{
	// ajax loading functionality	
	$('.navbar .loader')
		.ajaxStart(function()
		{ 
			var self = this;
			if($(this).prop('complete-animation-to'))
			{
				clearTimeout($(this).prop('complete-animation-to'));
				$(this).removeClass('complete');
			}
			$(this).addClass('active');
		})
		.ajaxComplete(function()
		{
			var self = this;
			$(this).removeClass('active').addClass('complete');
			$(this).prop('complete-animation-to', setTimeout( function(){ $(self).removeClass('complete'); }, 2000 ));
		})
	
	// use a deferred object to resolve the API URL and show content or alert message
	var urlDfd = new $.Deferred,
		resetDfd = function()
		{
			urlDfd = new $.Deferred;
			// when url deferred is complete, we're going to present the application or application failiure
			$.when(urlDfd).then(app, appFail);
			return urlDfd;
		}
	
	// get URL from cookie
	if( document.cookie.search(/api-url=([^;]+);/g) != -1 )
		resetDfd().resolve(document.cookie.replace(/api-url=([^;]+);.*/g, '$1'))
	
	// dialog to input URL
	var urlDialog = $($.tmpl('#request-dialog-tmpl', {})).dialog
	({
		autoOpen: false,
		width: 560,
		modal: true,
		open : resetDfd,
		buttons : 
		[{ 
			text: "Accept", 
			class: "btn btn-primary", 
			click: function()
			{
				var apiUrl = $(this).find('#api-url').val();
				console.log("xx", apiUrl)
				urlDfd.resolve(apiUrl);
				$(this).dialog('close');
			}
		},
		{
			text: "Cancel",
			class: "btn btn-warning",
			click: function()
			{
				urlDfd.reject();
				$(this).dialog('close')
			}
		}],
		close: function()
		{
			if( urlDfd.state() == 'pending' ) urlDfd.reject();
		}
	});
	
	$(document).data('url-dialog', urlDialog);
	$(document).on('click', '#alert-set-url, #menu-api-url', function(){ urlDialog.dialog('open'); return false; });
	$(document).on('click', '.alert a.close', function(){ $(this).parents('.alert:eq(0)').remove(); });
	
	if(urlDfd.state() != 'resolved')
		urlDialog.dialog('open');
	
});