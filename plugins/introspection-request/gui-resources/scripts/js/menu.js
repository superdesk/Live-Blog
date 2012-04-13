define(['jquery','jquery/superdesk','jquery/rest'], function ($,superdesk)
{
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.request')
		.done(function(actions)
		{
			$(actions).each(function()
			{
				if(this.Path == 'modules.request.list' && this.ScriptPath)
				{
					require([superdesk.apiUrl+this.ScriptPath]);
					/*(new superdesk.presentation).run(this.ScriptPath, superdesk.layouts.list.clone());
					return false;*/
				}
			});
		});
});