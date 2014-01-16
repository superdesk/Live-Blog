define([
	'gizmo/superdesk', 
	config.guiJs('livedesk', 'models/autocollection'),
    config.guiJs('livedesk', 'models/post')
], function( Gizmo, AutoCollection, Post ) {

    return Gizmo.Register.AutoCollection.extend({ 
		model: Gizmo.Register.Post,
	}, { register: 'AutoPosts' });
});