define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    'tmpl!superdesk/desks>task/add'
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
            $(this.el).appendTo($.superdesk.layoutPlaceholder);
            $('.modal', this.el).modal();
            $('input', this.el).val('');
        },
        init: function()
        {
            this.render();
        },
        render: function()
        {
            var self = this;
            $(self.el).tmpl('superdesk/desks>task/add', function(){ console.log(self.el.html()); });
        },
        save: function(evt)
        {
            evt.preventDefault();
            this.el.modal('hide');
        }
    }),
    
    addView = new AddView;
    
    return { init: function(){ addView.activate(); }};
});