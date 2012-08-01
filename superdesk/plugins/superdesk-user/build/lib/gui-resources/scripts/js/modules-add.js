var presentation = this,
app = function()
{
	$('#area-main').html(layout)

	var userForm, selectedUser;
	// get user and display its form
	var userFormHtml = presentation.view.render("#tpl-user-update-main", {});
	userForm = presentation.form.add(userFormHtml, 'User');
	$('#area-content', layout).html(userForm);
		
	// run user.update's subsequent actions 
	/*superdesk.getActions('modules.user.update.*')
	.done(function(actions)
	{
		$(actions).each(function()
		{ 
			presentation.run(this.ScriptPath, layout, {userId: args.userId, users: args.users})
		});
	});*/
	
	$(document)
	.off('click.superdesk-user', '#submit-main')
	.on('click.superdesk-user', '#submit-main', function(event)
	{
		args.users.insert(userForm.serialize())
			.success(function(){ console.log(arguments) })
			.error(function(){ console.log('error', arguments) })
		event.preventDefault();
	})
}

superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/user/templates/add.html').done(app)
		
