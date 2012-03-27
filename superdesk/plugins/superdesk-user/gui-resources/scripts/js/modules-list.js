var users,
	presentation = this;
var app = function()
{
	$('#area-main').html(layout);
	users = new $.rest(superdesk.apiUrl + '/resources/Superdesk/User').xfilter('Id, Name')
		.done(function(users)
		{
			$('#area-content', layout)
				.tmpl($("#tpl-user-list", superdesk.tmplRepo), {users: users, scriptPath: args.updateScript});
		})
}

this.view.load('user/templates/list.html').done(function(){ app() })

// edit button functionality 
$(document)
.off('click.superdesk', '.user-list .btn-edit')
.on('click.superdesk', '.user-list .btn-edit', function(event)
{
	presentation
		.setScript(args.updateScript)
		.setLayout(superdesk.layouts.update.clone())
		.setArgs({users: users, userId: $(this).attr('user-id')})
		.run()
	event.preventDefault();
});