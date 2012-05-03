define
([
  'jquery', 'jquery/tmpl', 'jquery/rest',
  'tmpl!livedesk>submenu',
], function($)
{
    app = {
        init: function(submenu) {
            setTimeout(function(){ 
                $(submenu).tmpl('submenu');
            }, 3000)
        }
    };
    return app;
});