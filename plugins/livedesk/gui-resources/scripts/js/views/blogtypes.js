 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/blogtype'),
    config.guiJs('livedesk', 'views/add-blogtype'),
    config.guiJs('livedesk', 'models/blogtypes'),
    
    'tmpl!livedesk>blogtype/blogtypes'
], function( $, Gizmo, BlogTypeView, AddBlogTypeView ) {  
   return Gizmo.View.extend({
        tmplData: {},
        events: {
            '[name="add-blogtype-modal"]': { 'click': 'addBlogTypeModal' }
        },
        init: function(){
            var self = this;
            if( !self.collection ) {
                self.collection = new Gizmo.Register.BlogTypes();
            }
            self.collection
                .on('read update', self.render, self)
                .xfilter('Id,Name,PostPosts')
                .sync();
            self.collection.model.on('add',self.addOne, self);
        },
        addOne: function(evt, model){
            var blogTypeView = new BlogTypeView({ _parent: this, model: model, tmplData: this.tmplData });
            this.el.find('.blogtype-list').append(blogTypeView.el)
        },
        addAll: function(evt, data) {
            data = (data === undefined) ? this.collection._list : data;
            for( var i = 0, count = data.length; i < count; i++ ){
                this.addOne(evt, data[i]);
            }
        },
        render: function(evt, data){
            if(!$('#add-blogtype').length) {
                $('body').append('<div id="content-add-blogtype"></div>');
            }
            var self = this;
            self.configBlogType = new AddBlogTypeView({ el: '#content-add-blogtype'});
            self.el
                .off(self.getEvent('click'), 'input[name="blogtypeselection"]')
                .on(self.getEvent('click'), 'input[name="blogtypeselection"]', function(){
                    self.el.find('input[name="blogtypeselection"]').each(function(i,val) {
                        var li = $(val).parents().eq(2);
                        if ($(val).prop('checked')===true) {
                          if (!li.hasClass("selected")) li.addClass("selected");
                        }
                        else {
                          if (li.hasClass("selected")) li.removeClass("selected");
                        }
                        
                    });
              });

            self.el.tmpl('livedesk>blogtype/blogtypes', this.tmplData, function(){
                self.addAll(evt, data);
            });
        },
        addBlogTypeModal: function(evt) {
            var self = this;
            self.configBlogType.switchModal(evt, 0);
        }
    });
});