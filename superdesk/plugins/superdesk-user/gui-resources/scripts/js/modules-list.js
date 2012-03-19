var users;
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

superdesk.getTmpl(superdesk.apiUrl+'/content/gui/superdesk/user/templates/list.html').done(function(){ app() })

// edit button functionality 
$(document)
.off('click.superdesk', '.user-list .btn-edit')
.on('click.superdesk', '.user-list .btn-edit', function(event)
{
	superdesk.applyScriptToLayout(args.updateScript, superdesk.layouts.update.clone(), {users: users, userId: $(this).attr('user-id')})
	event.preventDefault();
});