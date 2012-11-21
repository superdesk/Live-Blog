define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/list-view'),
    config.guiJs('media-archive', 'types/image/common'),
    'tmpl!media-archive>types/image/list'
],
function($, superdesk, giz, ItemView)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    ImageView = ItemView.extend
    ({
        tmpl: 'media-archive>types/image/list',
        editClass: common.edit,
        viewClass: common.view
    });
    
    return ImageView;
});

