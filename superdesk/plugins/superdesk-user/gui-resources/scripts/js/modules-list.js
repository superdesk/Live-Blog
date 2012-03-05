$(function()
{
	new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=modules.user.list')
		.done(console.log)
});