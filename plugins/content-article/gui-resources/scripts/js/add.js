define
([
    'jquery',
    'gizmo/superdesk',
    config.guiJs('content-article', 'models/article'),
    'gizmo/superdesk/action',
    'tmpl!superdesk/content-article>add'
],
function($, giz, Article, Action)
{
    var
    AddView = giz.View.extend
    ({
        events:
        {
            "[data-action='save']": { 'click': 'save' }
        },
        activate: function()
        {
            this.el.addClass('modal modal-wide fade').modal();
        },
        init: function()
        {
            this.render();
        },
        render: function()
        {
            var self = this;
            $(self.el).tmpl('superdesk/content-article>add');
        },
        save: function()
        {
            var article = new Article;
            article
                .set
                ({
                    Creator: localStorage.getItem('superdesk.login.id'),
                    Author: localStorage.getItem('superdesk.login.id'),
                    Content: JSON.stringify({Title: $('form [name="title"]', this.el).val(), Lead: '', Body: ''})
                })
                .sync()
                .done(function()
                { 
                    Action.initApp('modules.article.edit', article.hash());
                });
        }
    }),
    
    addView = new AddView;
    
    return { init: function(){ addView.activate(); }};
});