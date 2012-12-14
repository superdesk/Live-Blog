define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/common'),
    'tmpl!media-archive>types/_default/grid'
],
function($, superdesk, giz, base)
{
    ItemView = base.item.extend({});
    return ItemView;
});

