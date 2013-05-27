define( 'providers/colabs', [ 
    'providers', 
    'jquery',
    'gizmo/superdesk',
    config.guiJs('livedesk', 'models/blog'),
    config.guiJs('livedesk', 'models/collaborator'),
    config.guiJs('superdesk/user', 'models/person'),
    config.guiJs('livedesk', 'action'),
    config.guiJs('superdesk/user', 'jquery/avatar'),
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/collaborators',
    'providers/colabs/adaptor',
    'tmpl!livedesk>providers/colabs',
    'tmpl!livedesk>providers/colabs/items' ],
  
function(providers, $, giz, Blog, Collaborator, Person, BlogAction)
{
    var config = { updateInterval: 10 },
        colabsList = [],
        colabsHidden = {},
        updateInterval = 0,
        intervalRunning = false,
        updateItemCount = 0,
        postDateList = [],
        userImages = [];
    
    var addUserImages = function()
    {
        for(var i=0; i<userImages.length; i++) 
            colabView.el.find('[data-colab-id="'+userImages[i].UserId+'"] figure')
                .html('<img src="'+userImages[i].Thumbnail+'" />');
    },
    
    getDraggableHelper = function(evt)
    {
        var listItem = $(evt.currentTarget),
            helperElem = $('<ul />').css('max-width', '38%');
        listItem.clone().appendTo(helperElem);
        return helperElem;
    },
    
    // single post item view
    PostView = giz.View.extend
    ({
        init: function(opts)
        {
            this.model.on('update', this.render, this);
			this.model.on('read', this.render, this);
			this.model.on('delete', this.remove, this); // TODO should remove from ColabView?
        },
        render: function(evt)
        {
            /*!
             * @TODO implement this with IsCollectionDeleted Method
             * Ugly hack to remove published posts.
             */
            if(this.model.get('PublishedOn') || (this.model.get('IsPublished') === 'True')) 
            {
                this.remove();
                return;
            }
            
            var self = this,
                post = this.model.feed(true);
			if($.type(post.Meta) === 'string')
				post.Meta = JSON.parse(post.Meta);			
			$.avatar.setImage(post, { needle: 'AuthorPerson.EMail', size: 36});

			$.tmpl('livedesk>items/item', { Post: post, Base: 'implementors/collaborators' }, 
                function(e,o) 
                {
                    self.setElement(o);
                    
                    /*!
                     * need to check if collaborator was previously hidden 
                     * because update events are triggered from all over the place and will
                     * render this again and show the element regardless of prev. status
                     */
                    if( colabsHidden[parseInt(post.Creator.Id)] ) self.el.addClass('hide');
                    
                    BlogAction.get('modules.livedesk.blog-post-publish')
                    .done(function(action) 
                    {
                        self.el.hasClass('draggable') && self.el.draggable
                        ({
                            addClasses: false,
                            revert: 'invalid',
                            containment:'document',
                            helper: getDraggableHelper, //'clone',
                            appendTo: 'body',
                            zIndex: 2700,
                            clone: true,
                            start: function(evt, ui) { $(this).data('post', self.model); }
                        });
                    })
                    .fail(function(){ el.removeClass('draggable'); });
                });
			
            return self;
        },
        
        remove: function()
        {
            var pos = this.colab.get('PostUnpublished')._list.indexOf(this.model),
                pos2 = this.colab._viewModels.indexOf(this.model.get('Id'));
            if( pos !== -1 )
                this.colab.get('PostUnpublished')._list.splice(pos,1);
            if( pos2 !== -1 )
                this.colab._viewModels.splice(pos2,1);
            this.el.remove();
        }
    }),
    // main view
    ColabView = giz.View.extend
    ({
        namespace: 'livedesk',
        events: 
        {
            //'.collaborators-header .feed-info .label': {'click': 'toggleHeader'},
            '.new-results': {'update': 'showNewResults'}
        },
        
        toggleHeader: function()
        {
            var colabId = $(this).attr('data-colab-id'),
                posts = $(this).parents('.collaborators-header')
                            .nextAll('.post-list').find('li[data-colab-id='+colabId+']');
            
            if($(this).data('is-off'))
            {
                delete colabsHidden[colabId];
                posts.removeClass('hide');
                $(this).addClass('label-info').data('is-off', false);
            }
            else
            {
                colabsHidden[parseInt(colabId)] = true;
                posts.addClass('hide'); 
                $(this).removeClass('label-info').data('is-off', true);
            }
        },
        /*!
         * @param e event
         * @param count
         * @param callback
         * @param wether to do update auto. or add a click-to-show button
         */
        showNewResults: function(e, count, callback, auto)
        {
            if( !$('.'+providers.colabs.className).parents('li:eq(0)').hasClass('active') )
                this.notifications.removeClass('hide').text(count);
            
            var self = $('.new-results', this.el),
                notifications = this.notifications,
                cb = function()
                { 
                    notifications.addClass('hide');
                    self.addClass('hide'); 
                    callback.apply(this);
                };
            auto ? cb() : self.removeClass('hide').text( count+" "+_('new items! Update') ).one('click.livedesk', cb);
        },
        
        init: function()
        {
            this.notifications = $('.'+providers.colabs.className).parents('li:eq(0)').find('.notifications');
            this.notifications.addClass('hide');
            localStorage.setItem('superdesk.config.providers.colabs.notify', 0);
            
            $('.post-list', this.el).html('');

            $(this.el).on('click', '.collaborators-header .feed-info .label', this.toggleHeader);

            var blog = giz.Auth(new Blog(this.blogUrl)), // authenticated blog model
                self = this;
            
            self.el.html('<p>'+_('Loading collaborators...')+'</p>');
            
            self.colabsList = [];
            
            blog.sync().done(function()
            {
                var collaborators = blog.get('Collaborator');
                collaborators.on('read', function()
                {
                    self.colabsList = this;
                    self.setupHeader.call(self, this);
                    self.setupColabStream.call(self, this); 
                });
                collaborators.xfilter('User.Id', 'User.FullName', 'User.EMail', 'PostUnpublished').sync();
            });
            
            $('.'+providers.colabs.className)
                .parents('li:eq(0)').find('.config-notif').off('click').on('click', self.configNotif);
            
            $('.'+providers.colabs.className)
                .parents('li:eq(0)').find('.config-notif')
                .attr('title',_('Click to turn notifications on or off <br />while this tab is hidden'))
                .tooltip({placement: 'right'});
        },
        
        /*!
         * update posts from collaborators,
         * call sync with cId.since parameter 
         */
        update: function()
        {
            var self = this;
            this.colabsList.each(function()
            {
                var colab = this,
                    post = colab.get('PostUnpublished');
                // get post list and sync it with the server
                this.get('PostUnpublished')
                    .xfilter('*,Author.Source.*,Creator.*')
                    .sync({data: {'cId.since': this._latestPost}})
                    .done(function(data){ colab._latestPost = parseInt(data.lastCId);self.readPostsHandle.call(post, colab, $.noop, self); });
            });
        },
        /*!
         * display list header
         */
        setupHeader: function(colabs)
        {
            $(this.el).tmpl('livedesk>providers/colabs', {Colabs: colabs.feed('json', true)});
        },
        /*!
         * initial - initial count of collaborators
         */
        readPostsHandle: function(colab, initColabHandle, view )
        {
            // list of new posts to append
            var appendPosts = [],
                self = this;
            this.each(function()
            {
                //console.log('Id',this.get('Id'));
                if( $.inArray( this.get('Id'), colab._viewModels ) === -1 && !this.get('DeletedOn'))
                {
                    appendPosts.push(this);
                    colab._viewModels.push(this.get('Id'));
                }
                var pCId = parseInt(this.get('CId'));
                // store last id
                if(!isNaN(pCId)) colab._latestPost = Math.max(colab._latestPost, pCId);
            });
            updateItemCount += appendPosts.length;
            
            appendPosts.length && 
            $('.new-results', view.el).trigger('update.livedesk', [updateItemCount, function()
            {
                $(appendPosts.reverse()).each(function()
                {
                    // TODO very inefficient, refactoring on server needed 
                    postDateList.push({ Date: this.get('CreatedOn'), Timestamp: (new Date(this.get('CreatedOn'))).getTime(), Id: this.get('Id') });
                    postDateList.sort(function(x, y){ return x.Timestamp >  y.Timestamp; });
                    for(var i=0; i<postDateList.length; i++)
                    {
                        if( parseInt(postDateList[i].Id) == parseInt(this.get('Id')) )
                        {
                            if( postDateList[i-1] )
                            {
                                (new PostView({ model: this, colab: colab })).render().el.insertBefore($('[data-post-id="'+postDateList[i-1].Id+'"]', view.el));
                                break;
                            }
                            else if( postDateList[i+1] )
                            {
                                (new PostView({ model: this, colab: colab })).render().el.insertAfter($('[data-post-id="'+postDateList[i+1].Id+'"]', view.el));
                                break;
                            }
                            else
                            {
                                $('.post-list', view.el).append( (new PostView({ model: this, colab: colab })).render().el );
                                break;
                            }
                        }
                    }
                    //if(this.get('IsPublished') !== 'True')
                    //    $('.post-list', view.el).prepend( (new PostView({ model: this, colab: colab })).render().el );
                });
                updateItemCount -= appendPosts.length;
            }, initColabHandle()]);
        },
        /*!
         * setup post list
         */
        setupColabStream: function(colabs)
        {
            var self = this,
                initColabCnt = colabs.count(),
                /*!
                 * used for breaking init. action, decrementing until 0
                 */
                initColabHandle = function()
                {
                    var ret = initColabCnt ? true : false;
                    initColabCnt -= 1; // decrement initial until 0 so we know when init is over and do not send
                    if(initColabCnt <= 0) initColabHandle = function(){ return false; }
                    return ret;
                }; 
            
            // collaboratos list
            colabs.each(function()
            {
                var colab = this;
                colab._latestPost = 0;
                colab._viewModels = [];
                colab.sync().done(function()
                { 
                    // hacking user image
                    (new Person(Person.prototype.url.get()+'/'+colab.get('User').get('Id')))
                    .on('read', function()
                    { 
                        var meta = this.get('MetaDataIcon')
                        meta.sync({data:{ thumbSize: 'medium' }}).done(function()
                        {  
                            userImages.push({UserId: colab.get('User').get('Id'), Thumbnail: meta.get('Thumbnail').href});
                        });
                    })
                    .sync();

                    // get posts for each collaborator
                    var post = colab.get('PostUnpublished');
                    post.xfilter('*,Author.Source.*,Creator.*')
                        .sync()
                        .done(function(data){
                            //console.log('data:',data); 
                            colab._latestPost = parseInt(data.lastCId)
                            self.readPostsHandle.call(post, colab, initColabHandle, self); 
                        });
                    // start the auto update timers
                    self.startAutoUpdate();
                });
                
            });
        },
        startAutoUpdate: function()
        {
            var self = this;
            clearInterval(updateInterval);
            updateInterval = setInterval(function()
            {
                var cnfNotif = localStorage.getItem('superdesk.config.providers.colabs.notify');
                if(!$('.post-list:visible', self.el).length && !parseFloat(cnfNotif)) 
                {
                    clearInterval(updateInterval);
                    return;
                }
                self.update(); 
            }, config.updateInterval*1000);
            
            return self;
        },
        render: function(){},
        /*!
         * configure notifications on/off
         */
        configNotif: function()
        {
            var cnfNotif = localStorage.getItem('superdesk.config.providers.colabs.notify');
            if( !parseFloat(cnfNotif) )
            {
                localStorage.setItem('superdesk.config.providers.colabs.notify', 1);
                $(this).removeClass('badge-info').addClass('badge-warning');
            }
            else
            {
                localStorage.setItem('superdesk.config.providers.colabs.notify', 0);
                $(this).removeClass('badge-warning').addClass('badge-info');
            }
        }
       
        
        
    });

    var colabView = null;
    $.extend( providers.colabs, { init: function(blogUrl)
    { 
        if( !colabView || (this.el.get(0) != colabView.el.get(0)) )
        {
            colabView = new ColabView({ el: this.el, blogUrl: blogUrl });
            return colabView.startAutoUpdate();
        }
        if( colabView ){  colabView.startAutoUpdate(); }
    }});
    
    return providers;
});