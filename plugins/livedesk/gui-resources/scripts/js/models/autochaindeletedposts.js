define([
	'gizmo/superdesk', 
	config.guiJs('livedesk', 'models/autocollection'),
    config.guiJs('livedesk', 'models/postdeleted')
], function( Gizmo, AutoCollection, PostDeleted ) {

    return Gizmo.Register.AutoCollection.extend({ 
		model: Gizmo.Register.PostDeleted,
	}, { register: 'AutoDeletePosts' });
});