$(function()
{
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.user.update.person')
		.done(function(actions)
		{
			$(actions).each(function()
			{
				if( this.Path.replace(/modules\.user\.update\.person\./, '').split('.').length == 1 && this.ScriptPath)
					$.ajax(superdesk.apiUrl+'/'+this.ScriptPath, {dataType: 'script'})
			})
		})
})