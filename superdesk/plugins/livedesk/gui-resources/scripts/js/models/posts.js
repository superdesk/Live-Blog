define(['gizmo/superdesk', config.guiJs('livedesk', 'models/post')], 
function(giz, Post)
{
    return giz.Collection.extend(Post);
});