define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/list-view'),
    config.guiJs('media-archive-audio', 'media-archive/common'),
    'tmpl!media-archive-audio>media-archive/list'
],
function($, superdesk, giz, ItemView, common)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    AudioView = ItemView.extend
    ({
        tmpl: 'media-archive-audio>media-archive/list',
        editClass: common.edit,
        viewClass: common.view
    });
    return AudioView;
});

