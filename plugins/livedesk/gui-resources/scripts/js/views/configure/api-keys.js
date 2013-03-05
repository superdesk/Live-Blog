 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/configure/api-key'),
    config.guiJs('livedesk', 'models/sources'),
    'tmpl!livedesk>configure/api-keys'
], function( $, Gizmo, ApyKeyView) {
   return Gizmo.View.extend({
        accepted: [
            'instagram',
            'flickr',
            'soundcloud'
        ],
        init: function() {
            var self = this;
            self._views = [];
            if( !self.collection ) {
                self.collection = new Gizmo.Register.Sources();
            }
            self.collection
                .on('read update', self.render, self)
                .xfilter('Id,Name,Key')
                .sync();
        },
        addOne: function(evt, model){
            if(model.get('Name') === 'internal')
                return;
            var apyKeyView = new ApyKeyView({ _parent: this, model: model });
            this._views.push(apyKeyView);
            this.el.find('[name="Sources"]').append(apyKeyView.el)
        },
        addAll: function(evt, data) {
            data = this.collection._list;
            for( var i = 0, count = data.length; i < count; i++ ){
                if(this.accepted.indexOf(data[i].get('Name')) !== -1 )
                this.addOne(evt, data[i]);
            }
        },
        render: function(evt, data) {
            var self = this,
            	data = {};
            self.el.tmpl('livedesk>configure/api-keys', data, function(){
                self.addAll(evt, data);
            });        	
        },
        save: function(evt) {
            for( var i = 0, count = this._views.length; i < count; i++ ){
                this._views[i].save(); 
            }
        }
    });
});