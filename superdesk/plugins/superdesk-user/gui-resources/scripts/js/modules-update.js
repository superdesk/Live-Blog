var app = function()
{
	$('#area-main').html(layout)

	args.users.from({Id: args.userId})
		.done(function(data)
		{
			$('#area-content', layout).tmpl($("#tpl-user-update-main", superdesk.tmplRepo), data)	
		});
		
	var d = $.Deferred($.noop).then(function(data)
	{
		$('#area-sidebar-right', layout).tmpl($("#tpl-user-update-logs", superdesk.tmplRepo), data)
	});
	d.resolve({logs: [{date: (new Date).toLocaleString(), event: 'logged in'}]})
	
	superdesk.getActions('modules.user.update.*')
	.done(function(actions)
	{
		$(actions).each(function()
		{ 
			superdesk.applyScriptToLayout(this.ScriptPath, layout, {userId: args.userId, users: args.users})
		});
	});
	
	$(document)
	.off('click.superdesk', '#submit-main')
	.on('click.superdesk', '#submit-main', function(event)
	{
		$.ajax
		({ 
			type: 'post',
			headers: {'X-HTTP-Method-Override': 'PUT'},
			data: { User: { Name: $('#area-content', layout).find('#data-user-name').val() } },
			url: superdesk.apiUrl + '/resources/Superdesk/User/'+args.userId,
		})
		.success(function(){ console.log(arguments) })
		.error(function(){ console.log('error', arguments) })
		event.preventDefault();
	})
}

superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/user/templates/update.html').done(app)
		
