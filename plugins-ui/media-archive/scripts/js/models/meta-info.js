define([ 'gizmo/superdesk',
         config.guiJs('media-archive', 'models/language')],
function(giz, Language)
{
    return giz.Model.extend
    ({ 
        url: new giz.Url('Archive/MetaInfo'),
        defaults:
        {
            Language: Language
        }
    });
});