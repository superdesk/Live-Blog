define
([
    'jquery',
    'gizmo/superdesk',
    config.guiJs('superdesk/article', 'models/article'),
    'gizmo/superdesk/action',
    'tmpl!superdesk/article>add'
],
function($, giz, Article, Action)
{
    var
    AddView = giz.View.extend
    ({
        events:
        {
            "form": { 'submit': 'save' },
            "[data-action='save']": { 'click': 'save' }
        },
        activate: function()
        {
            this.el.addClass('modal modal-wide fade').modal();
            $('input', this.el).val('');
        },
        init: function()
        {
            this.render();
        },
        render: function()
        {
            var self = this;
            $(self.el).tmpl('superdesk/article>add');
        },
        save: function(evt)
        {
            evt.preventDefault();
            this.el.modal('hide');
            var article = new Article;
            article
                .set
                ({
                	Creator: localStorage.getItem('superdesk.login.id'),
                	Author: localStorage.getItem('superdesk.login.id'),
                    Content: JSON.stringify({Title: $('form [name="title"]', this.el).val(), Lead: '', Body: ''})
                })
                .xfilter('Id')
                .sync()
                .done(function()
                { 
                    $.superdesk.navigation.bind( 'article/'+article.get('Id'), function()
                    {
                        Action.initApp('modules.article.edit', article.hash());
                    }, '' );
                });
        }
    }),
    
    addView = new AddView;
    
    return { init: function(){ addView.activate(); }};
});