define([
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/posts')
], function( Gizmo )
{
    return Gizmo.Model.extend({
    	defaults: { 
    		PostPosts: Gizmo.Register.Posts
    	}
	}, { register: 'BlogType' });
});