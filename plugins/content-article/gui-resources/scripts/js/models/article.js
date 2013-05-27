define(['gizmo/superdesk', 
		config.guiJs('superdesk/article', 'models/target-types')], function(giz, TargetTypeCollection)
{ 
    return giz.Model.extend({
    	url: new giz.Url('Content/Article'),
    	defaults: {
    		TargetType: TargetTypeCollection
    	},
    	publishSync: function()
		{
			var publishHref = this.href+'/Publish';
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(publishHref).update({},{headers: {}}).done(function(data){
					//self._parse(data);
					self.Class.triggerHandler('publish', self);
					self.triggerHandler('publish', self);
					self.sync();
				});
			return ret;
		},
		unpublishSync: function()
		{
			var publishHref = this.href+'/Unpublish';
			var
				self = this,
				dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(publishHref).update({},{headers: {}}).done(function(data){
					//self._parse(data);
					self.Class.triggerHandler('unpublish', self);
					self.triggerHandler('unpublish', self);
					delete self.data.PublishedOn;
					self.sync();
				});
			return ret;
		}
	})
});