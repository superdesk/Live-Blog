define(['gizmo/superdesk', config.guiJs('livedesk', 'models/posttype')], function(Gizmo)
{
    return Gizmo.Collection.extend({ model: Post });
});