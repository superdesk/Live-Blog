// set up scripts from modules.user.* action
$(function()
{
	superdesk.getActions('modules.user.*')
	.done(function(actions)
	{
		// superdesk.navigation.bind(actions)
		
		var listPath, updatePath;
		$(actions).each(function()
		{  
			if( this.Path == 'modules.user.list' ) listPath = this.ScriptPath;
			if( this.Path == 'modules.user.update' ) updatePath = this.ScriptPath;
		});
		
		// superdesk.presentation.prototype.view.prefix = apiUrl+'/content/superdesk/';
		(new superdesk.presentation)
			.setScript(listPath)
			.setLayout(superdesk.layouts.list.clone())
			.setArgs({updateScript: updatePath})
			.run();
		
	});
});