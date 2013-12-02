define(['gizmo/superdesk',
	config.guiJs('livedesk', 'models/status')

], function(Gizmo) {

	return Gizmo.Collection.extend({
		url: new Gizmo.Url('Data/PostVerification'),
		model: Gizmo.Register.Status
	}, { register: 'Statuses' } );
});