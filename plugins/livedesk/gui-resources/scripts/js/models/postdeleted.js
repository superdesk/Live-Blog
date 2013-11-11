define([ 
	'gizmo/superdesk', 
	config.guiJs('livedesk', 'models/post')
	],
function(Gizmo, Person)
{
    // Post
	return Gizmo.Register.Post.extend({
		isDeleted: function(){
        	return this._forDelete || !this.data.DeletedOn;
        }
	}, { register: 'PostDeleted' } );
});