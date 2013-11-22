 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'models/languages'),   
    'tmpl!livedesk>base/languages',
], function( $, Gizmo) {
   
   return Gizmo.View.extend({
        tmpl: 'livedesk>base/languages',
        tmplData: {},
        init: function(){
            var self = this;
            if( !self.collection ) {
                self.collection = Gizmo.Auth(new Gizmo.Register.Languages());
                //self.collection = new Gizmo.Register.Languages();
            }
            self.collection
                .on('read update', self.render, self)
                .xfilter('Id,Name,Code')
                .sync();
        },
        render: function(evt, data){
            var self = this,
                data = { Languages: this.collection.feed() };
            $.extend( data, self.tmplData );
            self.el.tmpl(self.tmpl, data);
        }
    });
});