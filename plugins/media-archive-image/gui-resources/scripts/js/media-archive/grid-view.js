define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/grid-view'),
    config.guiJs('media-archive-image', 'media-archive/common'),
    'tmpl!media-archive-image>media-archive/grid',
    'tmpl!media-archive-image>media-archive/grid-hover'
],
function($, superdesk, giz, ItemView, common)
{
    var
    /*!
     * @see gizmo/views/list/ItemView
     */
    ImageView = ItemView.extend
    ({
        tmpl: 'media-archive-image>media-archive/grid',
        hoverTmpl: 'media-archive-image>media-archive/grid-hover',
        editClass: common.edit,
        viewClass: common.view
    });
    return ImageView;
});

