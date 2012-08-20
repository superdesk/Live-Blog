requirejs.config({
	paths: { 
		'providers': 'lib/livedesk/scripts/js/providers', 
		'livedesk/models': 'lib/livedesk/scripts/js/models', 
		'livedesk/collections': 'lib/livedesk/scripts/js/collections/' 
} });
define
([
  'jquery', 'jquery/superdesk',
  'gizmo/superdesk',
  config.guiJs('livedesk', 'models/blog'),
  'jquery/tmpl', 'jquery/rest',
  'tmpl!livedesk>submenu'
], function($, superdesk, Gizmo, Blog)
{
    var Blogs = Gizmo.Collection.extend({model: Blog, href: new Gizmo.Url('LiveDesk/Blog') }), 
        b = Gizmo.Auth(new Blogs());
    b.href.decorate('%s/Administered');
    
    var SubmenuView = Gizmo.View.extend
    ({
        init: function()
        {
            this.model.on('read update', this.render, this);
        },
        refresh: function()
        {
            this.model.xfilter('Title, Id').sync();
        },
        render: function()
        {
            $(this.menu).on('click', '#submenu-liveblogs-create', function()
            {
                superdesk.showLoader();
                superdesk.getAction('modules.livedesk.add')
                .done(function(action)
                {
                    action.ScriptPath &&
                        require([superdesk.apiUrl+action.ScriptPath], function(AddApp){ addApp = new AddApp(); });
                });  
            });
            $(this.menu).on('click', '.submenu-blog', function()
            {
                superdesk.showLoader();
                var theBlog = $(this).attr('data-blog-link');
                superdesk.getAction('modules.livedesk.edit')
                .done(function(action)
                {
                    action.ScriptPath && 
                        require([superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(theBlog); });
                });
            });
            this.menu.tmpl('livedesk>submenu', {Blogs: this.model.feed()}); 
        }
    });
    
    var subMenu = new SubmenuView({model: b});
    return {
        init: function(submenu, menu)
        { 
            subMenu.menu = $(submenu);
            //subMenu.setElement($(submenu, menu)).refresh();
            subMenu.refresh();
            return subMenu; 
        }
    };
});