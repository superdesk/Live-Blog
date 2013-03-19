define(['gizmo/superdesk'], function(giz)
{ 
    return giz.Model.extend({
    	url: new giz.Url('Content/Article'),
    	publishSync: function()
		{
			var publishHref = this.href+'/Publish';
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(publishHref).update({},{headers: {}}).done(function(data){
					self._parse(data);
					self.Class.triggerHandler('publish', self);
				});
			return ret;
		}
	})
});