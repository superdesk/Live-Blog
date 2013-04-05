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
        firstTime: true,
        metaBk: {},
        publish: function(evt) {
            var self = this;
            var before = $('.annotation.top', self.el).html();
            var after = $('..annotation.bottom', self.el).html();

            if ( self.firstTime ) {
                self.metaBk = self.data.Meta;
                self.firstTime = false;
            } else {
                //not the first time
            }

            self.metaBk.annotation = { before: before, after: after };
            self.data.Meta = JSON.stringify(self.metaBk);
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
            console.log(this.sourceTemplate);
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