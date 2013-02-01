define([ 'gizmo/superdesk', config.guiJs('superdesk/user', 'models/person')],
function(Gizmo, Person)
{
    // Post
	return Gizmo.Model.extend
	({
	    defaults: 
	    {
	        AuthorPerson: Person
	    },
	    insertExcludes: [ 'AuthorPerson' ],
	      
		url: new Gizmo.Url('/Post'),
		
		orderSync: function(id, before)
		{
			var reorderHref = this.href+'/Post/'+id+'/Reorder?before='+before;
//			console.log(reorderHref);
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
				removeHref = removeHref.replace(/LiveDesk\/Blog\/[\d]+/,'Data')
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
		publishSync: function()
		{
			var publishHref = this.href+'/Publish';
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(publishHref).insert({},{headers: { 'X-Filter': 'CId, Order'}}).done(function(data){
					self._parse(data);
					self.Class.triggerHandler('publish', self);
				});
			return ret;
		},
		unpublishSync: function()
		{
			var publishHref = this.href+'/Unpublish';
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(publishHref).insert({},{headers: { 'X-Filter': 'CId, Order'}}).done(function(data){
					delete self.data["PublishedOn"];
					self.triggerHandler('unpublish');
					self._parse(data);
					self.Class.triggerHandler('unpublish', self);
				});
			return ret;
		}
	}, { register: 'Post' } );
});