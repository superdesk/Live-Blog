 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'models/languages'),
    
    'tmpl!livedesk>add/languages',
], function( $, Gizmo) {
   
   return Gizmo.View.extend({
    
        init: function(){
            var self = this;
            if( !self.collection ) {
                self.collection = new Gizmo.Register.Languages();
            }
            self.collection
                .on('read update', self.render, self)
                .xfilter('Id,Name')
                .sync();
        },
        render: function(evt, data){
            this.el.tmpl('livedesk>add/languages', { Languages: this.collection.feed() });
        }
    });
});