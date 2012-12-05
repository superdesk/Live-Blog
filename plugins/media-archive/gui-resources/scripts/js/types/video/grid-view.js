define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/grid-view'),
    'tmpl!media-archive>types/video/grid'
],
function($, superdesk, giz, ItemView)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    AudioView = ItemView.extend
    ({
        tmpl: 'media-archive>types/video/grid'
    });
    
    return AudioView;
});

