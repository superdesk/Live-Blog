define([ 'gizmo/superdesk'],
function(Gizmo)
{
    // Post
	return Gizmo.AuthModel.extend({
		url: new Gizmo.Url('/Post'),
		order: function(id, before){
			var reorderHref = this.href+'/Post/'+id+'/Reorder?before='+before;
			console.log(reorderHref);
			var
				self = this,  
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(reorderHref).update();
			return ret;
		}
	}, { register: 'Post' } );
	/*
    return Gizmo.AuthModel.extend
    ({ 
		url: new Gizmo.Url('/Post'),
		defaults:
        { 
            Author: Collaborator,
            Blog: Blog,
            Creator: User,
            PostType: PostType
        }
    }, { register: 'Post' } );*/
});