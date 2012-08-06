define([ 'gizmo/superdesk'],
function(Gizmo)
{
    // Post
	return Gizmo.Model.extend({
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
		}/*,
		sync: function(data)
		{
			var self = this,
				ret = Gizmo.Model.prototype.sync.call(this, data);
			ret.done(function(){
				if(self.data.DeletedOn) {
                    self.triggerHandler('delete');
                    self._uniq && self._uniq.remove(self.hash());					
				}
			});
			return ret;
		}*/	
	}, { register: 'Post' } );
});