define([
    'gizmo/superdesk', 
    config.guiJs('livedesk', 'models/user')
], function( Gizmo, User ) {

    return Gizmo.Collection.extend({ 
		url: new Gizmo.Url('HR/User'),
		model: Gizmo.Register.User
	}, { register: 'Users' });
});