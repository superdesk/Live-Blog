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
            new $.rest(superdesk.apiUrl + '/resources/LiveDesk/Blog/').xfilter('Title,Id').done(function(blogs)
            { 
                $(submenu).tmpl('submenu', {Blogs: blogs}, function()
                { 
                    var createBtn = $(this).find('#submenu-liveblogs-create');
                    createBtn.off('click.livedesk')
                        .on('click.livedesk', function()
                        { 
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
                            var theBlog = $(this).attr('data-blog-link');
                            superdesk.getActions('modules.livedesk.*')
                            .done(function(actions)
                            {
                                require([superdesk.apiUrl+'/content/gui/superdesk/livedesk/scripts/js/edit-live-blogs.js'],
                                function(EditApp){ new EditApp(theBlog) });
                            });
                        });
                });
            });
        }
    };
    return app;
});