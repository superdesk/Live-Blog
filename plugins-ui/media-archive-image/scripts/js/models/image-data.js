define([ 'gizmo/superdesk', 
         config.guiJs('media-archive', 'models/meta-data'),
         config.guiJs('media-archive-image', 'models/image-info-list')],
function(giz, MetaData, ImageInfoList)
{
    return MetaData.extend
    ({  
        url: new giz.Url('Archive/ImageData'),
        defaults: 
        {
            ImageInfo: ImageInfoList
        },
        infoNode: 'ImageInfo'
    });
});