define(['gizmo/superdesk',
	config.guiJs('livedesk', 'models/status')

], function(Gizmo) {

		return Gizmo.Collection.extend({
			model: Gizmo.Register.Status
		}, { register: 'Statuses' } );
});