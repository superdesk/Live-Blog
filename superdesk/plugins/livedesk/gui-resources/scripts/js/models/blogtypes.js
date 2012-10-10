define(['gizmo', config.guiJs('livedesk', 'models/blogtype')], function(Gizmo)
{
    return Gizmo.Collection.extend({ model: BlogType },{ register: 'BlogTypes' });
});