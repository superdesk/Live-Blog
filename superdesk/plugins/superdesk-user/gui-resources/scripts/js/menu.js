// set up scripts from modules.user.* action
$(function()
{
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.user.*')
		.done(function(actions)
		{
			// superdesk.navigation.bind(actions)
			
			var listPath, updatePath;
			$(actions).each(function()
			{  
				if( this.Path == 'modules.user.list' ) listPath = this.ScriptPath;
				if( this.Path == 'modules.user.update' ) updatePath = this.ScriptPath;
			})
			superdesk.applyScriptToLayout(listPath, superdesk.layouts.list, { updateScript: updatePath })
		});
});