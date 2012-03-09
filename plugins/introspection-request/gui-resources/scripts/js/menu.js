$(function()
{
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.request')
		.done(function(actions)
		{
			$(actions).each(function()
			{
				if(this.Path == 'modules.request.list' && this.ScriptPath)
				{
					superdesk.applyScriptToLayout(this.ScriptPath, superdesk.layouts.list)
					return false;
				}
			})
		});
});