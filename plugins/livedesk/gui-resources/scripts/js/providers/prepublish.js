define([
    'jquery',
    'gizmo/superdesk',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/prepublish'
], function($, Gizmo) {
    return Gizmo.View.extend({
        events: {
            '.btn.publish': { 'click': 'publish' },
            '.btn.cancel': { 'click': 'cancel' },
            'a.close': { 'click': 'close' }
        },
        init: function()
        {
        },
        cancel: function(evt) {
            var self = this;
            self.parent = null;
            self.el.remove();
        },
        publish: function(evt) {
            var self = this;
            if($.type(self.data.Meta) === 'string')
                self.data.Meta = JSON.parse(self.data.Meta);
            self.data.Meta.annotation = { before: $('.annotation.top', self.el).html(), after: $('.annotation.bottom', self.el).html()};
            self.data.Meta = JSON.stringify(self.data.Meta);
            self.parent.insert(self.data, self);
            //$('.actions', self.el).addClass('hide');            
        },
        close: function(evt) {
            var self = this;
            $('#delete-post .yes')
                .off(self.getEvent('click'))
                .on(self.getEvent('click'), function(){
                    self.parent = null;
                    self.el.remove();
                });
        },
        render: function()
        {
            var self = this;
            if ( typeof this.data.Meta.annotation == 'undefined' ) {
                this.data.Meta.annotation = "<br />";
            }
            $.tmpl('livedesk>items/item', {
                    Base: 'implementors/prepublish',
                    Item: this.sourceTemplate,
                    Post: this.data
                }, function(e, o) { 
                    self.setElement(o);
            });
        }
    });
});