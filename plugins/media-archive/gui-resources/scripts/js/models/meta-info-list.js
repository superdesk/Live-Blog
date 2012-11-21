define([ 'gizmo/superdesk', config.guiJs('media-archive', 'models/meta-info') ],
function(giz, MetaInfo)
{
    return giz.Collection.extend({ model: MetaInfo });
});