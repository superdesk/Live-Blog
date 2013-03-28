requirejs.config({
	paths: { 
		'providers': config.gui('livedesk/scripts/js/providers'), 
		'livedesk/models': config.gui('lib/livedesk/scripts/js/models'), 
		'livedesk/collections': config.gui('lib/livedesk/scripts/js/collections/') 
} });
define
([
  'jquery', 'jquery/superdesk',
  'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    'gizmo/superdesk/action',
  config.guiJs('livedesk', 'models/blog'),
  'jquery/tmpl', 'jquery/rest',
  'tmpl!livedesk>submenu',
  'tmpl!livedesk>error-notif'
], function($, superdesk, Gizmo, BlogAction, Action, Blog)
{
    var Blogs = Gizmo.Collection.extend({model: Blog, href: new Gizmo.Url(localStorage.getItem('superdesk.login.selfHref')+'/Blog') }), 
        b = Gizmo.Auth(new Blogs());
    
    var SubmenuView = Gizmo.View.extend
    ({
        init: function()
        {
            this.model.on('read update', this.render, this);
            this.model.on('insert', this.refresh, this);
            this.router = new Backbone.Router;
            this.router.route('live-blog/:id', 'live-blog-edit', function(id) {
                var blogUrl = '/resources/LiveDesk/Blog/' + id;
                BlogAction.setBlogUrl(blogUrl);
                BlogAction.get('modules.livedesk.edit').
                    done(function(action) {
                        superdesk.showLoader();
                        if (!action) {
                            return;
                        }

                        require([action.get('Script').href], function(EditApp){ EditApp(blogUrl); });
                    }).
                    fail(function() {
                        $.tmpl('livedesk>error-notif', {Error: _('You cannot perform this action')}, function(e, o) {
                            var o = $(o);
                            $('#area-main').append(o);
                            $('.close', o).on('click', function(){ $(o).remove(); });
                            setTimeout(function(){ $(o).remove(); }, 3000);
                        });
                    });
            });

            this.router.route('liveblog-archive', 'liveblog-archive', function() {
                superdesk.showLoader();
                Action.
                    get('modules.livedesk.archive').
                    done(function(action) {
                        require([action.get('Script').href], function(app){ new app(); });
                    });
            });

            // TODO: this must be called once menu is prepared and routers are set. but where?
            Backbone.history.start({root: "/content/lib/core/start.html"});
        },

        refresh: function()
        {
            this.model.href = localStorage.getItem('superdesk.login.selfHref')+'/Blog';
            this.model._list = [];
            this.model.xfilter('Title, Id').sync();
        },

        render: function()
        {
            
            $(this.menu).on('click', '#submenu-liveblogs-create', function(event)
            {
                Action.get('modules.livedesk.add')
                .done(function(action)
                {
                    superdesk.showLoader();
                    action.get('Script') &&
                        require([action.get('Script').href], function(AddApp){ addApp = new AddApp(); });
                }); 
                event.preventDefault();
            });

            var self = this;

            /*!
             * apply template and go to selected blog if any
             */
            this.menu.tmpl('livedesk>submenu', {Blogs: this.model.feed()}, function()
            {
                // hide create if no right
                Action.get('modules.livedesk.add').fail(function(){ $('#submenu-liveblogs-create', self.menu).hide(); });
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
