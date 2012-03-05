var app = function()
{
	$('#area-main').html(layout)
	
	var d = $.Deferred($.noop).then(function(data)
	{
		$('#area-content', layout).append($.tmpl("#tpl-user-update-main", data))
	});
	d.resolve({Name: 'Billy'})
	var d = $.Deferred($.noop).then(function(data)
	{
		$('#area-sidebar-right', layout).append($.tmpl("#tpl-user-update-logs", data))
	});
	d.resolve({logs: [{date: (new Date).toLocaleString(), event: 'logged in'}]})
}

new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.user.update')
	.done(function(actions)
	{
		$.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/user/templates/update.html')
			.done(app)
		
		$(actions).each(function()
		{
			if( this.Path.replace(/modules\.user\.update\./, '').split('.').length == 1 && this.ScriptPath)
				$.ajax(superdesk.apiUrl+'/'+this.ScriptPath, {dataType: 'script'})
		})
	})
