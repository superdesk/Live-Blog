define([ 'gizmo/superdesk', 
    config.guiJs('livedesk', 'models/theme')
],
function(Gizmo)
{
    return Gizmo.Collection.extend({
    	url: new Gizmo.Url('LiveDesk/BlogTheme'),
    	model: Gizmo.Register.Theme
    }, { register: 'Themes' } );
});