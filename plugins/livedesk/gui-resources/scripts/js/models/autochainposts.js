define([
	'gizmo/superdesk', 
	config.guiJs('livedesk', 'models/autocollection'),
    config.guiJs('livedesk', 'models/postchain')
], function( Gizmo, AutoCollection, PostChain ) {

    return Gizmo.Register.AutoCollection.extend({ 
		model: Gizmo.Register.PostChain,
	}, { register: 'AutoChainPosts' });
});