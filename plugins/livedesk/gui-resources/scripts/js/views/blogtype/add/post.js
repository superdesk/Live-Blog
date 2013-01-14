define([
    'jquery', 
    'gizmo/superdesk',
    'tmpl!livedesk>blogtype/add/post'
], function( $, Gizmo) {

    return Gizmo.View.extend({
        tmplData: {},
        tagName: 'li',
        events: {
            '[name="post-edit"]': { 'click': 'edit' },
            '[name="post-remove"]': { 'click': 'remove' }
        },
        init: function(){
            var self = this;
            self.model
                .off('read update', self.render)
                .on('read update', self.render, self);
            this.render();
        },
        edit: function(evt) {
            this._parent._parent.editPost(evt, this.model);
        },
        remove: function(evt) {
            var self = this;
            self._parent.removeOne(self.model);
            self.model.remove();
            self.el.remove();
        },
        render: function(evt, data){
            var self = this,
                data = self.model.feed();            
            $.extend(data, self.tmplData);
            $.tmpl('livedesk>blogtype/add/post', data, function(e, o){
                self.setElement(o);
            });
        }        
    });
});