define
([
    'gizmo/superdesk',
    config.guiJs('media-archive', 'models/meta-data')
], 
function(giz, MetaData)
{ 
    return giz.Model.extend
    ({ 
        url: new giz.Url('Content/ArticleFile'),
        defaults: 
        {
            MetaData: MetaData
        }
    });
});