define([ 'gizmo/superdesk', config.guiJs('media-archive', 'models/language') ],
function(giz, Language)
{
    return giz.Collection.extend({ model: Language, href: new giz.Url('Localization/Language') });
});