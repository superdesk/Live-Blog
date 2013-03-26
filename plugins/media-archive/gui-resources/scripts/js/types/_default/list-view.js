define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/common'),
    'tmpl!media-archive>types/_default/list'
],
function($, superdesk, giz, base)
{
    var ItemView = base.item.extend({tmpl: 'media-archive>types/_default/grid'});
    return ItemView;
});

