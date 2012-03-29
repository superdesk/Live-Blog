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

this.view.load('user/templates/list.html').done(app)

// edit button functionality 
$(document)
.off('click.superdesk-user-list', '.user-list .btn-primary')
.on('click.superdesk-user-list', '.user-list .btn-primary', function(event)
{
	presentation
		.setScript(args.updateScript)
		.setLayout(superdesk.layouts.update.clone())
		.setArgs({users: users, userId: $(this).attr('user-id')})
		.run();
	event.preventDefault();
});

$(document)
.off('click.superdesk-user-list', '#btn-add-user')
.on('click.superdesk-user-list', '#btn-add-user', function(event)
{
	presentation
		.setScript(args.addScript)
		.setLayout(superdesk.layouts.update.clone())
		.setArgs({users: users})
		.run()
})
