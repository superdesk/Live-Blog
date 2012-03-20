var presentation = this,
app = function()
{
	args.users.get('Person').xfilter('FirstName,LastName,Id,Address')
	.done(function(data)
	{
		var content = '';
		$(data.PersonList).each(function()
		{
			content += $.tmpl($("#tpl-person-user-update-main", superdesk.tmplRepo), this)
		})
		$('#area-content', layout).append(content);
	});
}

superdesk.getActions('modules.user.update.person.*')
.done(function(actions)
{
	$(actions).each(function()
	{ 
		presentation.setScript(this.ScriptPath)
			.setLayout(layout)
			.setArgs({userId: args.userId})
			.run();
	});
})


superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/person/templates/user-update.html').done(app)