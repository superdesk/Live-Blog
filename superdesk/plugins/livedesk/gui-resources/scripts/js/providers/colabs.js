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
        init: function(opts)
        {
            this.model.on('update', this.render, this);
			this.model.on('read', this.render, this);
			this.model.on('delete', this.remove, this); // TODO should remove from ColabView?
        },
        render: function()
        {
            var self = this;
            $.tmpl( 'livedesk>providers/colabs/items', {Posts: this.model.feed('json')}, function(e, o)
            {
                self.setElement(o);
               
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
        },
        remove: function()
        {
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
                            .nextAll('.search-result-list').find('li[data-colab-id='+colabId+']');

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

            $(this.el).on('click', '.collaborators-header .feed-info .label', this.toggleHeader);

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
        /*!
         * initial - initial count of collaborators
         */
        readPostsHandle: function(initial, colab)
        {
            // list of new posts to append
            var appendPosts = [],
                self = this;
            this.each(function()
            {
                if( $.inArray( this.get('Id'), colab._viewModels ) === -1 )
                {
                    appendPosts.push(this);
                    colab._viewModels.push(this.get('Id'));
                }
                var pCId = parseInt(this.get('CId'));
                if(!isNaN(pCId)) colab._latestPost = Math.max(colab._latestPost, pCId);
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
        },
        /*!
         * setup post list
         */
        setupColabStream: function(colabs)
        {
            var self = this,
                initial = colabs.count(); // used for breaking init. action, decrementing until 0
            // collaboratos list
            colabs.each(function()
            {
                var colab = this;
                colab._latestPost = 0;
                colab._viewModels = [];
                colab.on('read', function()
                { 
                    // get posts for each collaborator
                    colab.get('Post').xfilter('*')
                        .on('read', function(){ self.readPostsHandle.call(this, initial, colab); })
                        .sync();
                    // start the auto update timers
                    self.startAutoUpdate();
                }).sync();
                
            });
        },
        startAutoUpdate: function()
        {
            var self = this;
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
            
            return self;
        },
        render: function()
        {
            console.log('render colabs')
        }
    });

    var colabView = null;
    $.extend( providers.colabs, { init: function(blogUrl)
    { 
        colabView = new ColabView({ el: this.el, blogUrl: blogUrl });
        this.init = function()
        {
            return colabView.startAutoUpdate(); 
        }; 
    }});
    
    return providers;
});