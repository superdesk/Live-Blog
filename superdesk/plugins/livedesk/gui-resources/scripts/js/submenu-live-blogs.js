requirejs.config({ paths: { providers:'gui/superdesk/livedesk/scripts/js/providers', } });
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
                            superdesk.getActions('modules.livedesk.*')
                            .done(function(actions)
                            {
                                $(actions).each(function()
                                {
                                    // and display add action
                                    if(this.Path == 'modules.livedesk.add' && this.ScriptPath)
                                        require([superdesk.apiUrl+this.ScriptPath], function(AddApp) {
                                            addApp = new AddApp();
                                        });
                                });
                            });
                        });
                    $(this).find('.submenu-blog').off('click.livedesk')
                        .on('click.livedesk', function()
                        {
                            superdesk.showLoader();
                            
                            var theBlog = $(this).attr('data-blog-link');
                            superdesk.getActions('modules.livedesk.*')
                            .done(function(actions)
                            {
                                $(actions).each(function()
                                {
                                    if(this.Path == 'modules.livedesk.edit' && this.ScriptPath)
                                        require([superdesk.apiUrl+this.ScriptPath], function(EditApp){ new EditApp(theBlog).render(); });
                                });
                            });
                        });
                });
            });
        }
    };
    return app;
});