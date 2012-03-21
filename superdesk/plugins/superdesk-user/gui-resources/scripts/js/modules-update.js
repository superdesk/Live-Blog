var presentation = this,
app = function()
{
	$('#area-main').html(layout)

	var userForm;
	// get user and display its form
	args.users.from({Id: args.userId})
		.done(function(data)
		{
			var userFormHtml = presentation.view.render("#tpl-user-update-main", data);
			userForm = presentation.form.add(userFormHtml, 'User');
			$('#area-content', layout).html(userForm);
		});
		
	var d = $.Deferred($.noop).then(function(data)
	{
		$('#area-sidebar-right', layout).tmpl($("#tpl-user-update-logs", superdesk.tmplRepo), data)
	});
	d.resolve({logs: [{date: (new Date).toLocaleString(), event: 'logged in'}]})
	
	// run user.update's subsequent actions 
	superdesk.getActions('modules.user.update.*')
	.done(function(actions)
	{
		$(actions).each(function()
		{ 
			presentation.run(this.ScriptPath, layout, {userId: args.userId, users: args.users})
		});
	});
	
	$(document)
	.off('click.superdesk', '#submit-main')
	.on('click.superdesk', '#submit-main', function(event)
	{
		args.users.insert( superdesk.apiUrl + '/resources/Superdesk/User/'+args.userId, userForm.serialize())
			.success(function(){ console.log(arguments) })
			.error(function(){ console.log('error', arguments) })
		event.preventDefault();
	})
}

superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/user/templates/update.html').done(app)
		
