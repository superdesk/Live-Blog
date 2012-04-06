// TODO set automatically on server startup
superdesk.apiUrl = "http://localhost:8080";

superdesk.navigation.init();

$(function()
{
	var buildMenu = function()
	{
		superdesk.getActions('menu')
		.done(function(menu)
		{
			var displayMenu = [];
			$(menu).each(function()
			{ 
				if( this.Path == 'menu' ) return true;
				var path = this.Path.split('.'); 
				this.Href = "/"+path.join('/');
				this.Name = path.join('-');
				displayMenu.push(this);
				var scriptPath = this.ScriptPath;
				$(document).off('click', 'a[href^="'+this.Href+'"]');
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