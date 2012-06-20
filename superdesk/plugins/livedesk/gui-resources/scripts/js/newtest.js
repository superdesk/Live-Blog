define(['newgizmo'], 
function(Gizmo)
{
	var Post = Gizmo.Model.extend({});
	var OwnPost = Gizmo.Collection.extend({
		model: Post,
		url: 'http://localhost:8080/resources/Superdesk/Collaborator/'
	});
	ownPost = new OwnPost;
	ownPost.sync();
});