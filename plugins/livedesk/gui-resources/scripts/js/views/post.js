requirejs.config({
	paths: { 
		'providers': config.gui('livedesk/scripts/js/providers')
	}
});
define
([ 
    'gizmo/superdesk',
    'jquery',
	'utils/extend',
    config.guiJs('livedesk', 'models/post'),
    config.guiJs('superdesk/user', 'jquery/avatar'),
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item'
], function(Gizmo, $) {
        /*!
         * used for each item of the timeline
         */
        return Gizmo.View.extend
        ({
            events: 
            {
                '': { sortstop: 'reorder' },
                'a.close': { click: 'removeDialog' },
                'a.unpublish': { click: 'unpublishDialog' },
                
                '.btn.cancel': {click: 'cancelActions', focusin: 'stopFocuseOut'},
                '.btn.publish': {click: 'save', focusin: 'stopFocuseOut'},
                '.editable': { focusin: 'edit'} //, focusout: 'focuseOut'}
            },
            showActions: function() {
                var self = this;
                self.el.find('.actions').removeClass('hide');
            },
            stopFocuseOut: function(evt) {
                var self = this,
                    actions = self.el.find('.actions');
                actions.data('focuseout-stop',true);
            },
            focuseOut: function(evt) {
                var self = this,
                    actions = self.el.find('.actions');
                    setTimeout(function(){
                        if(!actions.data('focuseout-stop')) {
                            self.hideActions(evt, 1000);
                        }
                        actions.removeData('focuseout-stop');
                    }, 100);
            },
            hideActions: function(evt, duration) {
                var self = this,
                    actions = self.el.find('.actions'),
                    duration = duration || 100;
                actions.fadeOut(duration, function(){
                    self.el.find('.editable').html(function(){
                        return $(this).data('previous');
                    });
                });
            },
            cancelActions: function(evt) {
                this.stopFocuseOut(evt);
                this.hideActions(evt);
            },
            /*!
             * subject to aop
             */
            preData: $.noop,
            save: function(evt)
            {
                var self = this,
                    actions = self.el.find('.actions'),
                    data = {
                        Meta: this.model.get('Meta'),
                        Content: $('.result-text.editable',this.el).html()
                };
                actions.data('focuseout-stop',true);
                if( !data.Content )
                    delete data.Content;
                if($.type(data.Meta) === 'string')
                    data.Meta = JSON.parse(data.Meta);
                data.Meta.annotation = { before: $('.annotation.top', self.el).html(), after: $('.annotation.bottom', self.el).html()};
                data.Meta = JSON.stringify(data.Meta);
                this.model.updater = this;
                this.model.set(data).sync();
                this.el.find('.actions').stop().fadeOut(100, function(){
                    $('.editable').removeData('previous');
                });
            },  
            edit: function(evt){
                var el = $(evt.target);
                this.el.find('.actions').stop(true).fadeTo(100, 1);
                if(!el.data('previous'))
                    el.data('previous', el.html());
            },
            init: function()
            {
                var self = this;
                self.el.data('view', self);
                self.xfilter = 'DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
                                   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, IsPublished, Creator.FullName';
                
                this.model
                    .on('delete', this.remove, this)
                    .off('unpublish').on('unpublish', function(evt) {
                        self.remove(evt);
                         /*
                         * @TODO: remove this
                         * Dirty hack to actualize the owncollection
                         */
                        var editposts = providers['edit'].collections.posts;
                        editposts.xfilter(editposts._xfilter).sync();
                    }, this)
                    .on('read', function()
                    {
                        //console.log('read: ');
                        /*!
                         * conditionally handing over save functionallity to provider if
                         * model has source name in providers 
                         */
                        try
                        {
                            var src = this.get("Author").Source.Name;
                            if( providers[src] && providers[src].timeline )
                            {
                                self.edit = providers[src].timeline.edit;
                                self.save = providers[src].timeline.save;
                            };
                        }
                        catch(e){ /*...*/ }
                        
                        self.render();
                    })
                    .on('set', function(evt, data)
                    {
                        /*!
                         * If the set triggering is the edit provider then don't update the view;
                         */
                        if(self.model.updater !== self) {
                            self.rerender();
                        }
                    })
                    .on('update', function(evt, data)
                    {
                        //console.log('update model: ',data);
                        /**
                         * Quickfix.
                         * @TODO: make the isCollectionDelete check in gizmo before triggering the update.
                         */
                        if( self._parent.collection.isCollectionDeleted(self.model) )
                            return;
                        if(data['Order'] && data['Order'] != self.order) {
                            self._parent.orderOne(self);
                        }
                        /*!
                         * If the updater on the model is the current view don't update the view;
                         */
                        if(self.model.updater === self) {
                            delete self.model.updater; return;
                        }
                        /*!
                         * If the Change Id is received, then sync the hole model;
                         */                      
                        self.rerender();
                        //; self.model.xfilter(xfilter).sync();
                        
                    })
                    .xfilter(self.xfilter);//.sync({data: {thumbSize: 'medium'}});
                    this.render();
            },
            
            rerender: function()
            {
                var self = this;
                self.el.fadeTo(500, '0.1', function(){
                    self.render().el.fadeTo(500, '1');
                });
            }, 
            render: function()
            {
                var self = this,
                    rendered = false,
                    post = self.model.feed(true);
                if ( typeof post.Meta === 'string') {
                    post.Meta = JSON.parse(post.Meta);
                }
                $.avatar.setImage(post, { needle: 'AuthorPerson.EMail', size: 36});
                $.tmpl('livedesk>items/item', { 
                    Base: self.tmplImplementor,
                    Post: post
                }, function(e, o) {
                    self.setElement(o);
                    self.el.triggerHandler('afterRender');
                });
                return this;
            },  
            remove: function(evt)
            {
                //console.log('evt: ',evt);
                var self = this;
                /**
                 * @TODO remove only this view events from the model
                 */
                //self.model.off('delete unpublish read update set');
                self._parent.removeOne(self);
                $(this.el).fadeTo(500, '0.1', function(){
                    self.el.remove();
                });
            },          
            removeDialog: function()
            {
                var self = this;
                $('#delete-post .yes')
                    .off(this.getEvent('click'))
                    .on(this.getEvent('click'), function(){
                        self.model.removeSync();
                    });

            },
            unpublishDialog: function(evt)
            {
                var self = this;
                $('#unpublish-post .yes')
                    .off(this.getEvent('click'))
                    .on(this.getEvent('click'), function(){
                        self.model.unpublishSync();
                    });

            }
        });    
});