define('providers/ads', [ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('livedesk', 'models/posts'),
    'providers/ads/adaptor',
    'tmpl!livedesk>providers/ads',
    'tmpl!livedesk>providers/ads/items'
], function(providers, $, Gizmo, Action)
{
    $.extend(providers.ads,  
    {
        init: function(theBlog) 
        {
            this.adaptor.init();
            var self = this,
                posts
            getAds = function()
            {
                posts = Gizmo.Auth(new Gizmo.Register.Posts(theBlog+'/PostType/advertisement/Post/Unpublished'));
                posts
                    .on('read update', function(evt,data){
                        $.tmpl('livedesk>providers/ads/items', {Posts: posts.feed()}, function(e, o)
                        {  
                            $('.search-result-list', self.el).prepend(o);
                            Action.get('modules.livedesk.blog-post-publish').done(function(action) {
                                $('.search-result-list li', self.el).draggable
                                ({
                                    helper: 'clone',
                                    appendTo: 'body',
                                    zIndex: 2700,
                                    start: function() 
                                    {
                                        $(this).data('data', self.adaptor.universal($(this)));
                                    }
                                });
                            }).fail(function(){
                                $('.search-result-list', self.el).find('.advertisement ').removeClass('draggable');
                            });
                        });
                    })
                    .xfilter('CreatedOn,Content,PublishedOn,Type,Id,CId')
                    .sync();
            };
            $(self.el).tmpl('livedesk>providers/ads', getAds);
        }
    });
    return providers;
});