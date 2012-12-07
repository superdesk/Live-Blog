define
([
  'jquery', 'jquery/superdesk',
  'gizmo/superdesk',
  config.guiJs('superdesk/article', 'models/article'),
  'jquery/tmpl', 'jquery/rest',
  'tmpl!superdesk/article>submenu'
], 
function($, superdesk, Gizmo, Article)
{
    var Articles = Gizmo.Collection.extend({model: Article, href: new Gizmo.Url('Superdesk/Article') }), 
        b = new Articles();
    
    var SubmenuView = Gizmo.View.extend
    ({
        /* events demo */
        events: 
        {
            'a.submenu-article': { click: 'menu' }
        },
        menu: function()
        {
            console.log('menu');
        },
        /* ----------- */
        
        init: function()
        {
            this.model.on('read update', this.render, this);
        },
        refresh: function()
        {
            this.model.xfilter('CreatedOn, Id, Slug, ArticleCtx').sync();
        },
        render: function()
        {
            /*!
             * we bind the event here 'cause we use a dynamic element 
             */
            $(this.menu).on('click', '.submenu-article', function(event)
            {
                superdesk.showLoader();
                var theArticle = $(this).attr('data-article-link'), self = this;
                superdesk.getAction('modules.article-demo.edit')
                .done(function(action)
                {
                    var callback = function()
                    { 
                        require([superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(theArticle); }); 
                    };
                    action.ScriptPath && superdesk.navigation.bind( $(self).attr('href'), callback, $(self).text() );
                });
                event.preventDefault();
            });
            
            var self = this;
            /*!
             * apply template and go to selected blog if any
             */
            this.menu.tmpl('superdesk/article>submenu', {Articles: this.model.feed()}, function()
            {
                if( superdesk.navigation.getStartPathname() == '') return false;
                self.menu.find('[href]').each(function()
                {
                    if( $(this).attr('href').replace(/^\/+|\/+$/g, '') == superdesk.navigation.getStartPathname()) 
                        $(this).trigger('click'); 
                });
            }); 
        }
    });
    
    var subMenu = new SubmenuView({model: b, el: $('.submenu-menu-article-demo')});
    return {
        init: function(submenu, menu)
        { 
            subMenu.menu = $(submenu);
            subMenu.refresh();
            return subMenu; 
        }
    };
});