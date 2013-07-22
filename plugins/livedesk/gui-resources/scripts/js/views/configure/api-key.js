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
            if(self.model.get('Name') === 'twitter') {
                try{
                    data.Source.Key = JSON.parse(data.Source.Key);
                } catch(e){
                    data.Source.Key = { 'ConsumerKey': '', 'ConsumerSecret': '' };
                }
            }
            $.tmpl('livedesk>configure/api-key',data, function(e,o){
                self.setElement(o);
            });
        },
        save: function(evt) {
            var self = this,
                key = self.el.find('[name="api-key"]').val();
            if(self.model.get('Name') === 'twitter') {
                key = JSON.stringify({ 
                    'ConsumerKey': this.el.find('[name="api-key-consumer-key"]').val(), 
                    'ConsumerSecret': this.el.find('[name="api-key-consumer-secret"]').val()
                });
            }
            self.model.set({ Key: key}).sync();
        }
    });
});