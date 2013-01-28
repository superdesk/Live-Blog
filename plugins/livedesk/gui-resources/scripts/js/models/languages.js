define([ 
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/language') 
], function( Gizmo ) {

    return Gizmo.Collection.extend({
    	url: new Gizmo.Url('Localization/Language'),
    	model: Gizmo.Register.Language 
    }, { register: 'Languages' } );

});