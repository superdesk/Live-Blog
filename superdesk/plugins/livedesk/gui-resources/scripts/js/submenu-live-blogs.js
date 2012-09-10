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
                event.preventDefault();
            });
            $(this.menu).on('click', '.submenu-blog', function(event)
            {
                superdesk.showLoader();
                var theBlog = $(this).attr('data-blog-link'), self = this;
                superdesk.getAction('modules.livedesk.edit')
                .done(function(action)
                {
                    var callback = function()
                    { 
                        require([superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(theBlog); }); 
                    };
                    action.ScriptPath && superdesk.navigation.bind( $(self).attr('href'), callback, $(self).text() );
                });
                event.preventDefault();
            });
            var self = this;
            /*!
             * apply template and go to selected blog if any
             */
            this.menu.tmpl('livedesk>submenu', {Blogs: this.model.feed()}, function()
            {
                var slashRE = /^\/+|\/+$/g;
                self.menu.find('[href]').each(function()
                {
                    if( $(this).attr('href').replace(slashRE, '') == superdesk.navigation.getStartPathname().replace(slashRE, '')) 
                        $(this).trigger('click'); 
                });
            }); 
        }
    });
    
    var subMenu = new SubmenuView({model: b});
    return {
        init: function(submenu, menu)
        { 
            subMenu.menu = $(submenu);
            subMenu.refresh();
            return subMenu; 
        }
    };
});