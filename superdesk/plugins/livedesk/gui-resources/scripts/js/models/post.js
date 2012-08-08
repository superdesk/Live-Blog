define([ 'gizmo/superdesk'],
function(Gizmo)
{
    // Post
	return Gizmo.Model.extend
	({
		url: new Gizmo.Url('/Post'),
		orderSync: function(id, before)
		{
			var reorderHref = this.href+'/Post/'+id+'/Reorder?before='+before;
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(reorderHref).update();
			return ret;
		},
		removeSync: function()
		{
			var removeHref = this.href;
			if(this.href.indexOf('LiveDesk/Blog') !== -1 ) {
				removeHref = removeHref.replace(/LiveDesk\/Blog\/\d/,'Superdesk')
			}
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(removeHref).remove().done(function() {
                    self.triggerHandler('delete');
                    self._uniq && self._uniq.remove(self.hash());
				});
			return ret;
		},
		publishSync: function(id)
		{
			var publishHref = this.href+'/Publish';
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(publishHref).insert();
			this.Class.triggerHandler('publish', this);
			return ret;
		}
	}, { register: 'Post' } );
});