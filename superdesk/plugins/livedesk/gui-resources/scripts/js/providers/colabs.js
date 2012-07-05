define( 'providers/colabs', 
[ 'providers', 'jquery', 'gizmo/superdesk', 
  
  'gui/superdesk/livedesk/scripts/js/models/blog',
  'gui/superdesk/livedesk/scripts/js/models/collaborator',
  
  'jquery/rest',
  'jquery/avatar',
  'providers/colabs/adaptor',
  'tmpl!livedesk>providers/colabs',
  'tmpl!livedesk>providers/colabs/items' ],
  
function(providers, $, giz, Blog, Collaborator)
{
    var config = { updateInterval: 30 },
        colabsList = [], 
        updateInterval = 0,
        intervalRunning = false;
    
    
    var ColabView = giz.View.extend
    ({
        events: 
        {
            '.collaborators-header': {'click': 'toggleHeader'},
            '.new-results': {'update.livedesk': 'showNewResults'}
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
        
        showNewResults: function()
        {
            var self = $(this);
            $(this).removeClass('hide')
                .text(count+" "+_('new items! Update')).one('click.livedesk', function()
                { 
                    self.addClass('hide'); 
                    callback.apply(this);
                });
        },
        
        initTab: function(blogUrl)
        {
            $('.search-result-list', this.el).html('');
            colabsList = [];
            var blog = new Blog(blogUrl),
                self = this;
            blog.on('read', function()
            { 
                var collaborators = this.get('Collaborator');
                collaborators.on('read', self.setupColabStream);
                collaborators.xfilter('Person.Id', 'Person.FullName', 'Person.EMail', 
                        'Post', 'PostPublished', 'PostUnpublished').sync();
            });
            blog.sync();
        },
        setupColabStream: function()
        {
            this.each(function()
            {
                var colab = this;
                colab.sync().done(function()
                { 
                    var person = colab.get('Person'),
                        posts = colab.get('Post');
                    //console.log(person, postPublished, postUnpublished);
                    $.when(person.xfilter('*').sync(), posts.xfilter('*').sync())
                    .then(function()
                    {
                        //for(var i=0; i<postList.length; i++)
                        //posts.each(function()
                        //{ 
                        //    colab._latestPost = Math.max(colab._latestPost, parseInt(posts[i].CId));
                        //});
                        $.tmpl( 'livedesk>providers/colabs/items', 
                                {Person: person.feed('json'), Posts: posts.feed('json')}, 
                        function(e, o)
                        {
                            
                            $('.search-result-list', self.el).prepend(o);
                            $('.search-result-list li.draggable', self.el).draggable
                            ({
                                helper: 'clone',
                                appendTo: 'body',
                                zIndex: 2700,
                                start: function() 
                                {
                                    $(this).data('post', self.adaptor.universal(this));
                                }
                            });
                          
                            clearInterval(updateInterval);
                            updateInterval = setInterval(function()
                            {
                                if(!$('.search-result-list:visible', self.el).length) 
                                {
                                    clearInterval(updateInterval);
                                    return;
                                }
                                update(); 
                            }, config.updateInterval*1000);
                      });
                        
                        
                    });
                });
            });
        },
        update: function()
        {
            $(colabsList).each(function()
            {
                console.log(this);
            });
        },
        
        render: function()
        {
            
        }
    });
    
    providers.colabs = new ColabView();

    return providers;
});