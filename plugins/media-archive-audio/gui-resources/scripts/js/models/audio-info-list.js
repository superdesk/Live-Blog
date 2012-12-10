define([ 'gizmo/superdesk',
         config.guiJs('media-archive', 'models/meta-info-list'),
         config.guiJs('media-archive-audio', 'models/audio-info') ],
function(giz, MetaInfoList, ImageInfo)
{
    return MetaInfoList.extend({ model: AudioInfo });
});