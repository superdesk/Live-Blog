define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/grid-view'),
    config.guiJs('media-archive-audio', 'media-archive/common'),
    'tmpl!media-archive-audio>media-archive/grid',
    'tmpl!media-archive-audio>media-archive/grid-hover'
],
function($, superdesk, giz, ItemView, common)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    AudioView = ItemView.extend
    ({
        tmpl: 'media-archive-audio>media-archive/grid',
        hoverTmpl: 'media-archive-audio>media-archive/grid-hover',
        editClass: common.edit,
        viewClass: common.view
    });
    return AudioView;
});

