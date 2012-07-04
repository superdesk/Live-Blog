define('providers/colabs', 
[ 'providers', 'jquery', 'jquery/rest', 'jquery/avatar',
  'providers/colabs/adaptor',
  'tmpl!livedesk>providers/colabs',
  'tmpl!livedesk>providers/colabs/items'
],
function(providers, $)
{
    var config = { updateInterval: 30 },
        colabsList = [], 
        updateInterval = 0,
        intervalRunning = false;
    
    $.extend(providers.colabs,  
    {
        init: function(theBlog) 
        {         
            $('.search-result-list', this.el).html('')
            colabsList = [];
            
            var self = this,
            setupHeader = function()
            {
                $('.collaborators-header', self.el)
                .off('click', 'span[data-colab-id]')
                .on('click', 'span[data-colab-id]', function()
                {
                    var colabId = $(this).attr('data-colab-id'),
                        posts = $('.collaborators-header', self.el).nextAll('.search-result-list').find('li[data-colab-id='+colabId+']');
                    
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
                $('.new-results', self.el).off('update.livedesk').on('update.livedesk', function(e, count, callback)
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
                    var colab = this,
                        updateRequest = new $.rest(colab).resetData()
                        .request({data: {'startEx.cId': colab._latestPost}})
                        .get('PostPublished').resetData().xfilter('CreatedOn,Content,PublishedOn,Type,Id,CId')
                        .get('PostUnpublished').resetData().xfilter('CreatedOn,Content,PublishedOn,Type,Id,CId')
                    .done(function(published, unpublished)
                    {
                        published = this.extractListData(published[0]);
                        unpublished = this.extractListData(unpublished[0]);
                        var postList = published.concat(unpublished);
                        
                        var appendPosts = [];
                        for(var i=0; i<postList.length; i++)
                        {
                            if(parseInt(postList[i].CId) > colab._latestPost)
                            {
                                appendPosts.push(postList[i]);
                                colab._latestPost = postList[i].CId;
                            }
                        }
                        updateItemCount += appendPosts.length; 
                        appendPosts.length &&
                        $('.new-results', self.el).trigger('update.livedesk', [updateItemCount, function()
                        {
                            $.tmpl('livedesk>providers/colabs/items', {Person: colab.Person, Posts: appendPosts}, function(e, o)
                            {
                                $('<ul>'+ o + '</ul>').find('li').each(function(){
                                    var postId = $(this).attr('data-post-id');
                                    $('.search-result-list li[data-post-id="' + postId + '"]', self.el).remove();
                                    $('.search-result-list', self.el).scrollTop(0).prepend($(this));
                                });
                                //$('.search-result-list', self.el).scrollTop(0).prepend(o);
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
                                updateItemCount -= appendPosts.length;
                            });
                        }]);
                    });
                });
            };

            new $.restAuth(theBlog).get('Collaborator').resetData().done(function(listData)
            {

                var colabsHrefs = this.extractListData(listData);
                $(colabsHrefs).each(function()
                { 
                    var c = new $.rest(this.href);

                    c.xfilter('Person.Id,Person.FullName,Person.EMail')
                    .done(function(colab)
                    {
                        var colabData = colab;

                        colab = $.avatar.parse(colab);
                        colab._latestPost = 0;
                        colabsList.push(colab);
                        if(colabsList.length == colabsHrefs.length)
                            $(self.el).tmpl('livedesk>providers/colabs', {Colabs: colabsList}, setupHeader);

                        new $.rest(colabData)
                            .get('PostPublished').resetData().request({data: { desc: 'createdOn'}}).xfilter('CreatedOn,Content,PublishedOn,Type,Id,CId')
                            .get('PostUnpublished').resetData().request({data: { desc: 'createdOn'}}).xfilter('CreatedOn,Content,PublishedOn,Type,Id,CId')
                        .done(function(published, unpublished)
                        {
                            published = this.extractListData(published[0]);
//                            console.log(published);
                            unpublished = this.extractListData(unpublished[0]);
//                            console.log(unpublished);
                            var postList = published.concat(unpublished);

                            for(var i=0; i<postList.length; i++)
                                colab._latestPost = Math.max(colab._latestPost, parseInt(postList[i].CId));
                            $.tmpl('livedesk>providers/colabs/items', {Person: colab.Person, Posts: postList}, function(e, o)
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
            });
            
            
        }
    });
    return providers;
});