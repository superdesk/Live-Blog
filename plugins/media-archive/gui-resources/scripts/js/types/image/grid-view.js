define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/grid-view'),
    config.guiJs('media-archive', 'types/image/common'),
    'tmpl!media-archive>types/image/grid'
],
function($, superdesk, giz, ItemView, common)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    ImageView = ItemView.extend
    ({
        tmpl: 'media-archive>types/image/grid',
        editClass: common.edit,
        viewClass: common.view
    });
    return ImageView;
});

