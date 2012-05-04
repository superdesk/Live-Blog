define
([
  'jquery', 'jquery/superdesk', 'jquery/tmpl', 'jquery/rest',
  'tmpl!livedesk>submenu',
  'tmpl!livedesk>layouts/livedesk'
], function($, superdesk)
{
    app = 
    {
        init: function(submenu) 
        {
            setTimeout(function()
            { 
                $(submenu).tmpl('submenu', function()
                { 
                    var createBtn = $(this).find('#submenu-liveblogs-create');
                    createBtn.off('click.livedesk')
                        .on('click.livedesk', function()
                        { 
                            // add layout
                            $('#area-main').tmpl('layouts/livedesk', function()
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
                                                listApp = new AddApp();
                                            });
                                    });
                                });
                            });
                        });
                });
            }, 3000);
        }
    };
    return app;
});