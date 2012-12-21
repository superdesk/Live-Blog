define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/list-view'),
    config.guiJs('media-archive-image', 'media-archive/common'),
    'tmpl!media-archive-image>media-archive/list',
    'tmpl!media-archive-image>media-archive/list-hover'
],
function($, superdesk, giz, ItemView, common)
{
    var
    /*!
     * @see gizmo/views/list/ItemView
     */
    ImageView = ItemView.extend
    ({
        tmpl: 'media-archive-image>media-archive/list',
        hoverTmpl: 'media-archive-image>media-archive/list-hover',
        editClass: common.edit,
        viewClass: common.view
    });
    return ImageView;
});

