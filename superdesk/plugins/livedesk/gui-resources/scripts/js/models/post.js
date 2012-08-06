define([ 'gizmo/superdesk'],
function(Gizmo)
{
    // Post
	return Gizmo.Model.extend({

		url: new Gizmo.Url('/Post'),
		order: function(id, before)
		{
			var reorderHref = this.href+'/Post/'+id+'/Reorder?before='+before;
			var
				self = this,  
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(reorderHref).update();
			return ret;
		},
		remove: function()
		{
			var removeHref = this.href;
			if(this.href.indexOf('LiveDesk/Blog') !== -1 ) {
				removeHref = removeHref.replace(/LiveDesk\/Blog\/\d/,'Superdesk')
			}
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(removeHref).remove();
			return ret;				
		}
	}, { register: 'Post' } );
});