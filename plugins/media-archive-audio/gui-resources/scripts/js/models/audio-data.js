define([ 'gizmo/superdesk', 
         config.guiJs('media-archive', 'models/meta-data'),
         config.guiJs('media-archive-audio', 'models/audio-info-list')],
function(giz, MetaData, AudioInfoList)
{
    return MetaData.extend
    ({  
        url: new giz.Url('Archive/AudioData'),
        defaults: 
        {
            AudioInfo: AudioInfoList
        },
        infoNode: 'AudioInfo'
    });
});