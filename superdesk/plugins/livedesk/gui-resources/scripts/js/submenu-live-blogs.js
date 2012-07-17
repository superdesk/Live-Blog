requirejs.config({
	paths: { 
		'providers': 'lib/livedesk/scripts/js/providers' 
} });
define
([
  'jquery', 'jquery/superdesk', 'jquery/tmpl', 'jquery/rest',
  'tmpl!livedesk>submenu'
], function($, superdesk)
{
    app = 
    {
        init: function(submenu) 
        {
            new $.restAuth('LiveDesk/Blog/Administered').xfilter('Title,Id').done(function(blogs)
            { 
                $(submenu).tmpl('livedesk>submenu', {Blogs: blogs}, function()
                { 
                    var createBtn = $(this).find('#submenu-liveblogs-create');
                    createBtn.off('click.livedesk')
                        .on('click.livedesk', function()
                        { 
                            superdesk.showLoader();
                            
                            // get modules.* actions
                            superdesk.getAction('modules.livedesk.add')
                            .done(function(action)
                            {
                                action.ScriptPath &&
                                    require([superdesk.apiUrl+action.ScriptPath], function(AddApp){ addApp = new AddApp(); });
                            });
                        });
                    $(this).find('.submenu-blog').off('click.livedesk')
                        .on('click.livedesk', function()
                        {
                            superdesk.showLoader();
                            
                            var theBlog = $(this).attr('data-blog-link');
                            superdesk.getAction('modules.livedesk.edit')
                            .done(function(action)
                            {
                                action.ScriptPath && 
                                    require([superdesk.apiUrl+action.ScriptPath], function(EditApp){ new EditApp(theBlog).render(); });
                            });
                        });
                });
            });
        }
    };
    return app;
});