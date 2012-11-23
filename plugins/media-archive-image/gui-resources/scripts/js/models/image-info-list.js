define([ 'gizmo/superdesk',
         config.guiJs('media-archive', 'models/meta-info-list'),
         config.guiJs('media-archive-image', 'models/image-info') ],
function(giz, MetaInfoList, ImageInfo)
{
    return MetaInfoList.extend({ model: ImageInfo });
});