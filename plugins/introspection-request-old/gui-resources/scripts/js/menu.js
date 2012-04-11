$(function()
{
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.request')
		.done(function(actions)
		{
			$(actions).each(function()
			{
				if(this.Path == 'modules.request.list' && this.ScriptPath)
				{
					(new superdesk.presentation).run(this.ScriptPath, superdesk.layouts.list.clone());
					return false;
				}
			});
		});
});