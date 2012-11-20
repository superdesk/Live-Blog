var presentation = this,
	app = function()
	{
		var personForms = [];
		// get user's person instances and display them
		args.users.get('Person').xfilter('FirstName,LastName,Id,Address')
		.spawn()
		.done(function(data, person)
		{
			var content = '';
			$(data.PersonList).each(function(i, person)
			{
				var personFormHtml = presentation.view.render("#tpl-person-user-update-main", $.extend({}, person, {index: i})),
					personForm = presentation.form.add(personFormHtml, 'Person');
				content += personForm.html();
				personForm.idPerson = person.Id
				personForms.push(personForm)
			})
			$(personForms).each(function(){ $('#area-content', layout).append(this); });
		});
		
		$(document)
		.off('click.superdesk-user-person', '#submit-main')
		.on('click.superdesk-user-person', '#submit-main', function(event)
		{
			$(personForms).each(function()
			{
				args.users.update(this.serialize(), superdesk.apiUrl + '/resources/Superdesk/Person/'+this.idPerson)
					.success(function(){ console.log(arguments) })
					.error(function(){ console.log('error', arguments) })
					event.preventDefault();
			});
		})
	}

superdesk.getActions('modules.user.update.person.*')
.done(function(actions)
{
	$(actions).each(function()
	{ 
		presentation.setScript(this.ScriptPath)
			.setLayout(layout)
			.setArgs(args)
			.run();
	});
})


superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/person/templates/user-update.html').done(app)