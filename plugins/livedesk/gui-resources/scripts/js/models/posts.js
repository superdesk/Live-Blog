define(['gizmo/superdesk', 
    config.guiJs('livedesk', 'models/post')
], function( Gizmo, Post ) {

    return Gizmo.Collection.extend({ 
		model: Gizmo.Register.Post,
        pendingPosts: [],
        init: function() {
            this.pendingPosts = [];
        },
		insertSync: function() {
            
            this.desynced = false;
            if( !(model instanceof Model) ) model = this.modelDataBuild(new this.model(model));
            this._list.push(model);
            model.hash();
            model.sync(this.href);
            return model;
		},
        feedPending: function(format, deep) {
            var ret = [],
                pos,
                post;
            for( var i = 0, count = this.pendingPosts.length; i < count; i++ ){
                post = this.pendingPosts[i];
                pos = this._list.indexOf(post);
                if( pos === -1 )
                    ret.push(post);
            }
            return ret;
        },
        removePending: function(model) {
            var self = this,
                pos = self._list.indexOf(model),
                ppos = self.pendingPosts.indexOf(model);
            if( pos !== -1 ) {
                self._list.splice(pos,1);
                self.pendingPosts.push(model);
            }
            if( ppos !== -1 )
                self.pendingPosts.splice(ppos,1);

        },
        savePending: function(href){
            var ret = [], 
                ppost, 
                posts;
            for( var i = 0, count = this.pendingPosts.length; i < count; i++ ){
                ppost = this.pendingPosts[i];
                if(ppost._new) {
                    ppost.href = href;
                    this.insert(ppost).done(function(data){
                        ppost._parseHash(data);
                    });
                } else {
                    ppost.sync();
                }
            }
            if(this.pendingPosts.length) {
                posts = this.pendingPosts.slice(0);
                this.pendingPosts = [];                
                this.triggerHandler('update',[posts]);

            }
            this.triggerHandler('addingspending');
            return ret;            
        },
        addPending: function(model) {
            this.desynced = false;
            if( !(model instanceof Gizmo.Model) ) model = this.modelDataBuild(new this.model(model));
            model.hash();
            var found = false,
                post;
            for( var i = 0, count = this.pendingPosts.length; i < count; i++ ){
                post = this.pendingPosts[i];
                if( post === model) {
                    found = true;
                    break;
                } 
            }
            if(!found)
                this.pendingPosts.push(model);
            this.triggerHandler('updatepending',[[model]]);
        }	
	}, { register: 'Posts' });
});