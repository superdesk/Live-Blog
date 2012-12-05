define([
	'gizmo/superdesk',
	'livedesk-embed/collections/posts'
], function( Gizmo ) {
	return Gizmo.Model.extend
	({
		defaults: 
		{
			//Post: Posts,
			PostPublished: Gizmo.Register.Posts
			//PostUnpublished: Posts
		}
	}, { register: 'Blog' } );
});