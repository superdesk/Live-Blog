define([
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/posts')
], function( Gizmo )
{
    return Gizmo.Model.extend({
    	url: new Gizmo.Url('LiveDesk/BlogType'),
    	defaults: { 
    		PostPosts: Gizmo.Register.Posts
    	}
	}, { register: 'BlogType' });
});