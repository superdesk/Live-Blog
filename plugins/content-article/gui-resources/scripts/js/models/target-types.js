define([
	'gizmo/superdesk',
	config.guiJs('superdesk/article', 'models/target-type'),
], function(giz, TargetType) {
	var TargetTypeCollection = giz.Collection.extend({
    	model: TargetType,
    	href: TargetType.prototype.url,
    	url: new giz.Url('Content/TargetType'),
    	update: function(key) {
			var self = this;
			var updateHref = this.href + encodeURIComponent(key);
			var dataAdapter = function() {
				return self.syncAdapter.request.apply(self.syncAdapter, arguments);
			};
            ret = dataAdapter(updateHref).update();
            return ret;
    	},
    	delete: function(key) {
			var self = this;
			var deleteHref = this.href + encodeURIComponent(key);
			var dataAdapter = function() {
				return self.syncAdapter.request.apply(self.syncAdapter, arguments);
			};
            ret = dataAdapter(deleteHref).remove();
            return ret;
    	}
    });
    
    return TargetTypeCollection;
});