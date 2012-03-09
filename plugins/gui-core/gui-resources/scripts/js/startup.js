// TODO set automatically on server startup
superdesk.apiUrl = "http://localhost:8080";

$(function()
{
	var buildMenu = function()
	{
		var menu = new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=menu')
		.done(function(menu)
		{
			// superdesk.navigation.bind(menu);

			var displayMenu = [];
			$(menu).each(function()
			{ 
				if( this.Path == 'menu' ) return true;
				var path = this.Path.split('.'); 
				this.Href = "/"+path.join('/');
				this.Name = path.join('-');
				displayMenu.push(this);
				var scriptPath = this.ScriptPath;
				$(document).on('click', 'a[href^="'+this.Href+'"]', function(event)
				{
					$.ajax(superdesk.apiUrl+'/'+scriptPath, {dataType: 'script'});
					event.preventDefault();
				});
			});
			$('#navbar-top').tmpl( '#navbar-tmpl', {menu: displayMenu} );
			
		});
	};
	
	$.when( superdesk.loadLayout('/content/lib/core/layouts/dashboard.html', 'dashboard'),
			superdesk.loadLayout('/content/lib/core/layouts/update.html', 'update'),
			superdesk.loadLayout('/content/lib/core/layouts/list.html', 'list') )
	.then(function()
	{
		buildMenu();
		$('#area-main').tmpl(superdesk.layouts.dashboard);
	});
});