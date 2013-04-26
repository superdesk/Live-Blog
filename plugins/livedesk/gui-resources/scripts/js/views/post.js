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
                        /*!
                         * If the updater on the model is the current view don't update the view;
                         */
                        if(self.model.updater === self) {
                            delete self.model.updater; return;
                        }
                        if(data['Order'])
                            self.order = parseFloat(data['Order']);
                        /*!
                         * If the Change Id is received, then sync the hole model;
                         */                      
                        if(isOnly(data, ['CId','Order'])) {
                            self.model.xfilter(self.xfilter).sync();
                        }
                        else {
                            self.rerender();
                        }
                        //; self.model.xfilter(xfilter).sync();
                        
                    })
                    .xfilter(self.xfilter);//.sync({data: {thumbSize: 'medium'}});
                    this.render();
            },
            
            reorder: function(evt, ui)
            {
                var self = this, next = $(ui.item).next('li'), prev = $(ui.item).prev('li'), id, order, newPrev = undefined, newNext = undefined;
                if(next.length) {
                    var nextView = next.data('view');
                    nextView.prev = self;
                    newNext = nextView;
                    id = nextView.id;
                    order = 'true';
                }
                if(prev.length){
                    var prevView = prev.data('view');
                    prevView.next = self;
                    newPrev = prevView;
                    id = prevView.id;
                    order = 'false';
                }
                self.tightkNots();
                self.prev = newPrev;
                self.next = newNext;
                self.model.orderSync(id, order);
                self.model.ordering = self;
                self.model.xfilter(self.xfilter).sync().done(function(data){
                    self.model.Class.triggerHandler('reorder', self.model);
                });
            },
            /**
             * Method used to remake connection in the post list ( dubled linked list )
             *   when the post is removed from that position
             */         
            tightkNots: function()
            {
                if(this.next !== undefined) {
                    this.next.prev = this.prev;
                }
                if(this.prev !== undefined) {
                    this.prev.next = this.next;             
                }
            },
            
            rerender: function()
            {
                var self = this;
                self.el.fadeTo(500, '0.1', function(){
                    self.render().el.fadeTo(500, '1');
                });
            },
            reorder: function()
            {
                var self = this, order = parseFloat(this.model.get('Order'));
                if(isNaN(order)) {
                    order = 0.0;
                }
                if ( !isNaN(self.order) && (order != self.order) && this.model.ordering !== self) {
                    var actions = { prev: 'insertBefore', next: 'insertAfter' }, ways = { prev: 1, next: -1}, anti = { prev: 'next', next: 'prev'}
                    for( var dir = (self.order - order > 0)? 'next': 'prev', cursor=self[dir];
                        (cursor[dir] !== undefined) && ( cursor[dir].order*ways[dir] < order*ways[dir] );
                        cursor = cursor[dir]
                    );
                    var other = cursor[dir];
                    if(other !== undefined)
                        other[anti[dir]] = self;
                    cursor[dir] = self;
                    self.tightkNots();
                    self[dir] = other;
                    self[anti[dir]] = cursor;
                    self.el[actions[dir]](cursor.el);
                }
                if(this.model.ordering === self)
                    delete this.model.ordering;
                self.order = order;
                self.id = this.model.get('Id');             
            }, 
            render: function()
            {
                var self = this,
                    rendered = false,
                    post = self.model.feed(true);
                self.reorder();
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
                self.tightkNots();
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