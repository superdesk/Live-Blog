define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/blogtype/add/post'),
    'tmpl!livedesk>blogtype/add/posts'
], function( $, Gizmo, PostView) {

    return Gizmo.View.extend({
        tmplData: {},
        init: function(){
            var self = this;
            //this._views = [];
            self.collection
                .off('read update addingspending updatepending', self.render)
                .on('read update addingspending updatepending', self.render, self);
            self.render();
        },
        removeOne: function(view) {
            var self = this;
            self.collection.removePending(view)
            //var pos = self._views.indexOf(view);
            //self._views.splice(pos,1);           
        },
        addOne: function(model) {
            //if( model.addBlogPost )
            //    return;
            var self = this,
                current = new PostView({ model: model, _parent: self });
            model.addBlogPost = current;
            //self._views.push(current);
            self.el.append(current.el);
        },
        render: function(evt, data){
            var self = this,
                data = this.collection.feedPending().concat(this.collection._list);
            //console.log(data);
            $.tmpl('livedesk>blogtype/add/posts', {}, function(e, o){
                self.setElement(o);
                for( var i = 0, count = data.length; i < count; i++ ){
                    self.addOne(data[i]);
                }
            });
        }        
    });
});