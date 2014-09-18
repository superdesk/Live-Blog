define([ 
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/general-setting') 
], function( Gizmo ) {

    return Gizmo.Collection.extend({
    	url: new Gizmo.Url('GeneralSetting'),
    	model: Gizmo.Register.GeneralSetting
    }, { register: 'GeneralSettings' } );
});