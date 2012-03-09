var app = function()
{
	$('#area-main').html(layout)

	new $.rest(superdesk.apiUrl + '/resources/Superdesk/User/' + args.userId)
		.done(function(data)
		{
			$('#area-content', layout).tmpl($("#tpl-user-update-main", superdesk.tmplRepo), data)	
		});
		
	var d = $.Deferred($.noop).then(function(data)
	{
		$('#area-sidebar-right', layout).tmpl($("#tpl-user-update-logs", superdesk.tmplRepo), data)
	});
	d.resolve({logs: [{date: (new Date).toLocaleString(), event: 'logged in'}]})
	
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.user.update.*')
		.done(function(actions)
		{
			$(actions).each(function()
			{ 
				superdesk.applyScriptToLayout(this.ScriptPath, layout, {userId: args.userId})
			});
		});
}

superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/user/templates/update.html').done(app)
		
