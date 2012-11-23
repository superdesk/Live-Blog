define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/list-view'),
    config.guiJs('media-archive-image', 'media-archive/common'),
    'tmpl!media-archive-image>media-archive/list'
],
function($, superdesk, giz, ItemView)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    ImageView = ItemView.extend
    ({
        tmpl: 'media-archive-image>media-archive/list',
        editClass: common.edit,
        viewClass: common.view
    });
    return ImageView;
});

