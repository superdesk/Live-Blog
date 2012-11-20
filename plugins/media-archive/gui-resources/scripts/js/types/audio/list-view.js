define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/list-view'),
    'tmpl!media-archive>types/audio/list'
],
function($, superdesk, giz, ItemView)
{
    /*!
     * @see gizmo/views/list/ItemView
     */
    AudioView = ItemView.extend
    ({
        tmpl: 'media-archive>types/audio/list'
    });
    
    return AudioView;
});

