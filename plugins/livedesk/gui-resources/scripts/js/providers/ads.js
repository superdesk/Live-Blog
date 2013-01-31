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
                posts.on('read update', function(evt,data){
                    console.log('evt: ',evt)
                }).sync();
            };
            $(self.el).tmpl('livedesk>providers/ads', getAds);
        }
    });
    return providers;
});