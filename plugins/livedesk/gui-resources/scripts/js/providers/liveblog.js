define([ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('livedesk', 'models/posts')
], function(providers, $, Gizmo, BlogAction)
{
    $.extend(providers.liveblog,  
    {
        init: function(theBlog) 
        {
			console.log('Hello');
        }
    });
    return providers;
});