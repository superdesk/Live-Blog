var presentation = this,
app = function()
{
	$('#area-main').html(layout)

	var form = function(){}
	form.prototype = 
	{
		add: function(html, nodeName)
		{
			if(!nodeName) return html;
			
			$(html).find('input, textarea, select').each(function()
			{
				var name = $(this).attr('name');
				$(this).attr('name', name.replace(/^([^\[]+)/, nodeName+'[$1]'))
			})
			return html
		}
	};
	
	args.users.from({Id: args.userId})
		.done(function(data)
		{
			var userForm = (new form).add($($.tmpl($("#tpl-user-update-main", superdesk.tmplRepo), data)), 'User');
			$('#area-content', layout).html(userForm)	
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
			presentation.run(this.ScriptPath, layout, {userId: args.userId, users: args.users})
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
		
