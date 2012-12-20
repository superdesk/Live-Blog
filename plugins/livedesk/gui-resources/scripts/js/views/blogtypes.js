 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/blogtype'),    
    config.guiJs('livedesk', 'models/blogtypes'),
    
    'tmpl!livedesk>blogtype/blogtypes',
], function( $, Gizmo, BlogTypeView ) {
   
   return Gizmo.View.extend({
        tmplData: {},
        init: function(){
            var self = this;
            if( !self.collection ) {
                self.collection = new Gizmo.Register.BlogTypes();
            }
            self.collection
                .on('read update', self.render, self)
                .xfilter('Id,Name,PostPosts')
                .sync();
        },
        addOne: function(model){
            var blogTypeView = new BlogTypeView({ model: model, tmplData: this.tmplData });
            this.el.find('.blogtype-list').append(blogTypeView.el)
        },
        addAll: function(evt, data) {
            data = (data === undefined) ? this.collection._list : data;
            for( var i = 0, count = data.length; i < count; i++ ){
                this.addOne(data[i]);
            }
        },
        render: function(evt, data){
            this.el.tmpl('livedesk>blogtype/blogtypes', this.tmplData );
            this.addAll(evt, data);
        }
    });
});