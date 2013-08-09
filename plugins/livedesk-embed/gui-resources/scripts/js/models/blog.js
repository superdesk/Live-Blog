define([
	'gizmo/superdesk',
	'collections/posts'
], function( Gizmo ) {
	return Gizmo.Model.extend({
		url: new Gizmo.Url('LiveDesk/Blog'),		
		defaults: {
			PostPublished: Gizmo.Register.Posts
		}
	}, { register: 'Blog' } );
});