define('providers/colabs', 
[ 'providers', 'jquery', 'jquery/rest',
  'tmpl!livedesk>providers/colabs',
  'tmpl!livedesk>providers/colabs-items'
],
function(providers, $)
{
    var config = { updateInterval: 3 },
        colabsList = [], 
        updateInterval = 0,
        intervalRunning = false;
    
    $.extend(providers.colabs,  
    {
        updateInterval: 0,       
        init: function(theBlog) 
        {         
            $('.search-result-list', this.el).html('');
            colabsList = [];
            
            var self = this,
            setupHeader = function()
            {
                $('.collaborators-header', self.el)
                .off('click', 'span[data-colab-id]')
                .on('click', 'span[data-colab-id]', function()
                {
                    var colabId = $(this).attr('data-colab-id'),
                        posts = $('.collaborators-header', self.el).nextAll('.search-result-list').find('li[data-colab-id!='+colabId+']');
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
                });  
                $('.new-results', self.el).on('update.livedesk', function(e, count, callback)
                {
                    var self = $(this);
                    $(this).removeClass('hide')
                        .text(count+" "+_('new items! Update')).one('click.livedesk', function()
                        { 
                            self.addClass('hide'); 
                            callback.apply(this);
                        });
                });
            },
            updateItemCount = 0,
            update = function()
            {
                $(colabsList).each(function()
                {
                    var colab = this;
                    new $.rest(colab.Collaborator.Post.Post.href).xfilter('Id, Content, CreatedOn, PublishedOn')
                    .done(function(postList)
                    {
                        var appendPosts = [];
                        for(var i=0; i<postList.length; i++)
                        {
                            if(parseInt(postList[i].Id) > colab._latestPost)
                            {
                                appendPosts.push(postList[i]);
                                colab._latestPost = postList[i].Id;
                            }
                        }
                        updateItemCount += appendPosts.length; 
                        appendPosts.length &&
                        $('.new-results', self.el).trigger('update.livedesk', [updateItemCount, function()
                        {
                            $.tmpl('livedesk>providers/colabs-items', {Person: colab.Collaborator.Person, Posts: appendPosts}, function(e, o)
                            {
                                $('.search-result-list', self.el).prepend(o);
                                updateItemCount -= appendPosts.length;
                            });
                        }]);
                    });
                });
            },
            blog = new $.rest(theBlog).get('Collaborator').done(function(listData)
            {
                var colabsHrefs = this.extractListData(listData);
                $(colabsHrefs).each(function()
                { 
                    new $.rest(this.href)
                    .xfilter('Collaborator.Person.FirstName,Collaborator.Person.LastName,Collaborator.Person.Id,Collaborator.Post')
                    .done(function(colab)
                    {
                        colab._latestPost = 0;
                        colabsList.push(colab);
                        if(colabsList.length == colabsHrefs.length)
                            $(self.el).tmpl('livedesk>providers/colabs', {Colabs: colabsList}, setupHeader);
                       
                        new $.rest(colab.Collaborator.Post.Post.href)
                        .xfilter('Id, Content, CreatedOn, PublishedOn')
                        .done(function(postList)
                        {
                            for(var i=0; i<postList.length; i++)
                                colab._latestPost = Math.max(colab._latestPost, parseInt(postList[i].Id));

                            $.tmpl('livedesk>providers/colabs-items', {Person: colab.Collaborator.Person, Posts: postList}, function(e, o)
                            {
                                $('.search-result-list', self.el).prepend(o);
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
            });
            
            
        }
    });
    return providers;
});