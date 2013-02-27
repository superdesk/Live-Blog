define
([
    'gizmo/superdesk', 'jquery', 
    config.guiJs('superdesk/article', 'models/article-ctx'),
    config.guiJs('superdesk/article', 'models/article'),
    'tmpl!superdesk/article>list',
    'tmpl!superdesk/article>item'
],
function(giz, $, ArticleCtx, Article)
{
    var dummyTypes = [{Id: 1, Name: 'Text'}, {Id: 2, Name: 'Web'}, {Id: 3, Name: 'Smartphone'}, {Id: 4, Name: 'Tablet'}],
    ItemView = giz.View.extend
    ({
        init: function()
        {
            //this.setElement($('<div />'));
        },
        render: function(ctx)
        {
            var cssClass = 'ctx-'+ctx.get('Type'),
                content = ctx.get('Content'),
                self = this;
            $.tmpl('superdesk/article>item', {ViewClass: cssClass, Content:content}, function()
            { 
                self.setElement($(arguments[1]));
            });
            return this;
        }
    }),
    ListView = giz.View.extend
    ({
        // --- models --- //
        article: null,
        contexts: null,
        // -------------- //
        events: 
        {
            '#article-views-ctrl li': {click: 'toggleView'}
        },
        toggleView: function(evt)
        {
            $(evt.target).parent().siblings().removeClass('active');
            var view = $('.ctx-'+$(evt.target).parent().addClass('active').attr('data-toggle-view'), $(this.el)).parent()
            view.removeClass('after').removeClass('before').addClass('now');
            view.prevAll('.article-view').removeClass('now').addClass('before');
            view.nextAll('.article-view').removeClass('now').addClass('after');
        },
        
        init: function()
        {
            // this.contexts = new (giz.Collection.extend({ model: ArticleCtx }));
            // and bind to events here, then on activate sync with their url from article
        },
        activate: function(href)
        {
            var self = this;
            this.article = new Article(href);
            this.contexts = this.article.get('ArticleCtx');
            this.contexts
                .xfilter('*')
                .sync(this.article.get('ArticleCtx').href)
                .done(function(){ self.render(); });
        },
        addItem : function(ctx)
        {
            $('#article-views-main', self.el).append((new ItemView).render(ctx).el);
        },
        render: function()
        {
            var data = {Types: dummyTypes},
                self = this;
            $.superdesk.applyLayout('superdesk/article>list', data, function()
            {
                // new ItemView for each models 
                self.contexts.each(function(){ self.addItem(this); });
            });
            $('#article-views-ctrl li:eq(0) a').trigger('click');
            $.superdesk.hideLoader();
        }
    });
    
    listView = new ListView({ el: '#area-main' }); 
    
    return function(article)
    {
        listView.activate(article);
    };
});