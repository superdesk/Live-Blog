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
            //added ability to change the content before publishing 
            if ( $('.result-text', self.el).hasClass('editable') ) {
                self.data.Content = $('.result-text', self.el).html();
            }

            self.data.Meta.annotation = { before: $('.annotation.top', self.el).html(), after: $('.annotation.bottom', self.el).html()};
            self.data.Meta = JSON.stringify(self.data.Meta);
            if ( self.data.Content ) {
                var conLen = self.data.Content.length;
                if ( conLen > 2800 ) {
                    //show warning message
                    self.data.Content = self.data.Content.substring(0, 2800) + ' ...';
                    var errorMessage = _('Maximum post lenght is 3000 characters, your post has been trimmed to fit that').toString();
                    $('.message-error', self.el).html(errorMessage).css('display', 'block');
                    setTimeout(function(){
                        self.parent.insert(self.data, self);
                    }, 1000)
                } else {
                    self.parent.insert(self.data, self);
                }
            } else {
                self.parent.insert(self.data, self);
            }
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