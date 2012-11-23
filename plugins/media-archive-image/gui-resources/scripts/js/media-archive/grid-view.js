define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/grid-view'),
    config.guiJs('media-archive-image', 'media-archive/common'),
    'tmpl!media-archive-image>media-archive/grid'
],
function($, superdesk, giz, ItemView, common)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    ImageView = ItemView.extend
    ({
        tmpl: 'media-archive-image>media-archive/grid',
        editClass: common.edit,
        viewClass: common.view
    });
    return ImageView;
});

