define([
	'gizmo/superdesk',
	config.guiJs('livedesk', 'models/post')
], function(Gizmo)
{
    return Gizmo.Model.extend({
    	PostPosts: Gizmo.Register.Posts
	}, { register: 'BlogType' });
});