define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/grid-view'),
    config.guiJs('media-archive-video', 'media-archive/common'),
    'tmpl!media-archive-video>media-archive/grid'
],
function($, superdesk, giz, ItemView, common)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    VideoView = ItemView.extend
    ({
        tmpl: 'media-archive-video>media-archive/grid',
        editClass: common.edit,
        viewClass: common.view
    });
    return VideoView;
});

