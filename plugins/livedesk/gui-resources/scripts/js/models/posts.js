define(['gizmo/superdesk', 
    config.guiJs('livedesk', 'models/post')
], function( Gizmo, Post ) {

    return Gizmo.Collection.extend({ 
		model: Gizmo.Register.Post,
        pendingPosts: [],
		insertSync: function() {
            
            this.desynced = false;
            if( !(model instanceof Model) ) model = this.modelDataBuild(new this.model(model));
            this._list.push(model);
            model.hash();
            model.sync(this.href);
            return model;
		},
        feedPending: function(format, deep) {
            var ret = [];
            for( var i in this.pendingPosts )
                ret[i] = this.pendingPosts[i].feed(format, deep);
            return ret;
        },
        savePending: function(href){
            var ret = [];
            for( var i in this.pendingPosts ) {
                this.pendingPosts[i].href = href;
                this.insert(this.pendingPosts[i]);
            }
            this.pendingPosts = [];
            return ret;            
        },
        clientAdd: function(model) {
            this.desynced = false;
            if( !(model instanceof Gizmo.Model) ) model = this.modelDataBuild(new this.model(model));
            model.hash();
            this.pendingPosts.push(model);
            this.triggerHandler('clientupdate',[[model]]);
        }	
	}, { register: 'Posts' });
});