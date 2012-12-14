define([ 'gizmo/superdesk', 
         config.guiJs('media-archive', 'models/meta-data'),
         config.guiJs('media-archive-video', 'models/video-info-list')],
function(giz, MetaData, VideoInfoList)
{
    return MetaData.extend
    ({  
        url: new giz.Url('Archive/VideoData'),
        defaults: 
        {
            VideoInfo: VideoInfoList
        },
        infoNode: 'VideoInfo'
    });
});