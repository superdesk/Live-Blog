define([
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/source'),
	], 
function( Gizmo )
{
    return Gizmo.Model.extend({
    	defaults: {
    		Source: Gizmo.Register.Source
    	}
	}, { register: 'Author' } );
});