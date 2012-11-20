define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/view'),
    'tmpl!media-archive>types/_default/list'
],
function($, superdesk, giz, View)
{
    ItemView = View.extend({});
    return ItemView;
});

