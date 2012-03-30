var countries,
	presentation = this;
var app = function()
{
	$('#area-main').html(layout);
	
	$('#area-content').html( $('<table class="table table-bordered table-striped country-list" />').datatable
	({
		templates: 
		{
			header: $("#tpl-country-list-header", superdesk.tmplRepo),
			footer: $("#tpl-country-list-footer", superdesk.tmplRepo),
			body: $("#tpl-country-list-body", superdesk.tmplRepo)
		},
		resource: new $.rest(superdesk.apiUrl + '/resources/Superdesk/Country').xfilter('Code, Name')
	}));
}

presentation.view.load('country/templates/list.html').done(app);

return;

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
