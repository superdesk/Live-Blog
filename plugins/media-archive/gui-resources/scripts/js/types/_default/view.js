define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk'
],
function($, superdesk, giz)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    ItemView = giz.View.extend
    ({
        model: null,
        tagName: 'div',
        render: function()
        {
            var self = this,
                data = this.model.feed();
            data.Content = function(chk, ctx)
            {
                return data.Thumbnail && data.Thumbnail.href ? '<img src="'+data.Thumbnail.href+'" />' : ''
            }
            $(this.el).tmpl(this.tmpl, {Item: data}).prop('model', this.model).prop('view', this);
            
            // TODO maybe this is better? 
            // $(this.el).tmpl(this.tmpl, {Item: this.model.feed()});
            // $(this.el).prop('model', this.model).prop('view', this);
            
            return this;
        },
        remove: function()
        {
            this.model.remove().sync();
        }
    });
    
    return ItemView;
});

