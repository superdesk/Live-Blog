define([ 
	'gizmo/superdesk', 
	config.guiJs('livedesk', 'models/post')
	],
function(Gizmo, Person)
{
    // Post
	return Gizmo.Register.Post.extend({}, { register: 'PostChain' } );
});