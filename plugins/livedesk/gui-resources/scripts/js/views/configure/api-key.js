 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'models/source'),
    'tmpl!livedesk>configure/api-key'
], function( $, Gizmo) {
   return Gizmo.View.extend({
        init: function() {
            this.render();
        },
        render: function(evt) {
            var self = this,
            	data = { Source: self.model.feed() };
            if(data.Source.Name === 'twitter') {
                data.Source.Key = JSON.parse(data.Source.Key);
            }
            $.tmpl('livedesk>configure/api-key',data, function(e,o){
                self.setElement(o);
            });
        },
        save: function(evt) {
            var self = this,
                key = this.el.find('[name="api-key"]').val();
            this.model.set({ Key: key}).sync();
        }
    });
});