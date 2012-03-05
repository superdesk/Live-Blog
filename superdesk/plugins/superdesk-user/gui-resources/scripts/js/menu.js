$(function()
{
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.user')
		.done(function(actions)
		{
			$(actions).each(function()
			{
				if(this.Path == 'modules.user.update' && this.ScriptPath)
				{
					$.applyScriptToLayout(this.ScriptPath, superdesk.layouts.update)
					return false;
				}
			})
		})
});