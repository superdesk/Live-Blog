define([ 'gizmo/superdesk',
         config.guiJs('media-archive', 'models/meta-info-list'),
         config.guiJs('media-archive-video', 'models/video-info') ],
function(giz, MetaInfoList, ImageInfo)
{
    return MetaInfoList.extend({ model: VideoInfo });
});