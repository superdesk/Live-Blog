define([ 'gizmo/superdesk', 
         config.guiJs('media-archive', 'models/meta-info')],
function(giz, MetaInfo)
{
    return MetaInfo.extend
    ({  
        url: new giz.Url('Archive/AudioInfo')
    });
});