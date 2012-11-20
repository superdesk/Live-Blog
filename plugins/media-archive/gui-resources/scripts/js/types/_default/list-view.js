define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    'tmpl!media-archive>types/_default/list'
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
            var self = this;
            $.tmpl(this.tmpl, {Item: this.model.feed()}, function(e, o)
            { 
                self.setElement(o); 
                $(self.el).prop('model', self.model).prop('view', self);
            });
            
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

