define( 'providers/colabs', 
[ 'providers', 'jquery', 'gizmo/superdesk', 
  
  config.guiJs('livedesk', 'models/blog'),
  config.guiJs('livedesk', 'models/collaborator'),
  
  'providers/colabs/adaptor',
  'tmpl!livedesk>providers/colabs',
  'tmpl!livedesk>providers/colabs/items' ],
  
function(providers, $, giz, Blog, Collaborator)
{
    var config = { updateInterval: 10 },
        colabsList = [], 
        updateInterval = 0,
        intervalRunning = false,
        updateItemCount = 0;
    
    // single post item view
    var PostView = giz.View.extend
    ({
        init: function()
        {
            var self = this;
            giz.Auth(this.model).on('update', function(){ self.render(true); });
        },
        render: function(update)
        {
            var self = this;
            $.tmpl( 'livedesk>providers/colabs/items', {Posts: this.model.feed('json')}, function(e, o)
            {
                var newItem = $(o);
                if(update) { $(self.el).replaceWith(newItem); self.el = newItem; }
                else self.el = newItem;
                
                // make draggable
                self.el.hasClass('draggable') && self.el.draggable
                ({
                    helper: 'clone',
                    appendTo: 'body',
                    zIndex: 2700,
                    start: function(){ $(this).data('post', providers.colabs.adaptor.universal(this)); }
                });
            });
            return self;
        }
    }),
    // main view
    ColabView = giz.View.extend
    ({
        namespace: 'livedesk',
        events: 
        {
            '.collaborators-header .feed-info .label': {'click': 'toggleHeader'},
            '.new-results': {'update': 'showNewResults'}
        },
        
        toggleHeader: function()
        {
            var colabId = $(this).attr('data-colab-id'),
                posts = $(this).nextAll('.search-result-list').find('li[data-colab-id='+colabId+']');
            
            if($(this).data('is-off'))
            {
                posts.show();
                $(this).addClass('label-info').data('is-off', false);
            }
            else
            {
                posts.hide(); 
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
            var self = $('.new-results', this.el),
                cb = function()
                { 
                    self.addClass('hide'); 
                    callback.apply(this);
                };
            auto ? cb() : self.removeClass('hide').text( count+" "+_('new items! Update') ).one('click.livedesk', cb);
        },
        
        init: function()
        {
            $('.search-result-list', this.el).html('');
            var blog = giz.Auth(new Blog(this.blogUrl)), // autheticated blog model
                self = this;
            
            self.el.html('<p>'+_('Loading collaborators...')+'</p>');
            
            self.colabsList = [];
            
            blog.on('read', function()
            {
                var collaborators = this.get('Collaborator');
                collaborators.on('read', function()
                {
                    self.colabsList = this;
                    self.setupHeader.call(self, this);
                    self.setupColabStream.call(self, this); 
                });
                collaborators.xfilter('Person.Id', 'Person.FullName', 'Person.EMail', 'Post').sync();
            });
            blog.sync();
        },
        
        update: function()
        {
            this.colabsList.each(function()
            {
                // get post list and sync it with the server
                this.get('Post').xfilter('*').sync({data: {'startEx.cId': this._latestPost}});
            });
        },
        
        /*!
         * display list header
         */
        setupHeader: function(colabs)
        {
            $(this.el).tmpl('livedesk>providers/colabs', {Colabs: colabs.feed('json', true)});
        },
        
        readPostsHandle: function()
        {
            
        },
        
        /*!
         * setup post list
         */
        setupColabStream: function(colabs)
        {
            var self = this,
                initial = colabs.count(); // used for breaking init. action
            // collaboratos list
            colabs.each(function()
            {
                var colab = this;
                
                colab._latestPost = 0;
                colab._viewModels = [];
                colab.on('read', function()
                { 
                    // get posts for each collaborator
                    // TODO isolate the callback
                    colab.get('Post').xfilter('*')
                        .on('read', function()
                        { 
                            // list of new posts to append
                            var appendPosts = [];
                            this.each(function()
                            {
                                if( $.inArray( this.get('Id'), colab._viewModels ) === -1 )
                                {
                                    appendPosts.push(this);
                                    colab._viewModels.push(this.get('Id'));
                                }
                                //console.log(this, Math.max(colab._latestPost, parseInt(this.get('CId'))));
                                colab._latestPost = Math.max(colab._latestPost, parseInt(this.get('CId')));
                            });
                            updateItemCount += appendPosts.length;
                            
                            appendPosts.length && $('.new-results', self.el).trigger('update.livedesk', [updateItemCount, function()
                            {
                                $(appendPosts).each(function()
                                { 
                                    $('.search-result-list', self.el).prepend( (new PostView({ model: this })).render().el );
                                });
                                updateItemCount -= appendPosts.length;
                            }, initial ? true : false]);
                            
                            initial -= 1; // decrement initial until 0 so we know when init is over and do not send
                            
                        }).sync();
                    
                    clearInterval(updateInterval);
                    updateInterval = setInterval(function()
                    {
                        if(!$('.search-result-list:visible', self.el).length) 
                        {
                            clearInterval(updateInterval);
                            return;
                        }
                        self.update(); 
                    }, config.updateInterval*1000);
                    
                }).sync();
                
            });
        },
        render: function()
        {
            
        }
    });

    $.extend( providers.colabs, { init: function(blogUrl){ new ColabView({ el: this.el, blogUrl: blogUrl }); } });
    
    return providers;
});