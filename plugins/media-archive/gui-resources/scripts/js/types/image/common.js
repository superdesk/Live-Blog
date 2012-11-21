define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    config.guiJs('media-archive', 'types/_default/common'),
    'tmpl!media-archive>types/image/edit',
    'tmpl!media-archive>types/image/view'
],
function($, superdesk, giz, base)
{
    var 
    Edit = base.edit.extend
    ({
        tmpl: 'media-archive>types/image/edit'
    }),
    View = base.view.extend
    ({
        tmpl: 'media-archive>types/image/view'
    });
    return {edit: Edit, view: View};
});

