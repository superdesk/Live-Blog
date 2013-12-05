define([
    'jquery', 
    'gizmo/superdesk'
], function( $, Gizmo) {

	var StatusesView = Gizmo.View.extend({
		init: function(){
			var self = this;
			// if(!self.collection) {
			// 	self.collection = Gizmo.Auth(new Gizmo.Register.Statuses());
			// }
			// self.collection
			// 	.on('read', self.render, self)
			// 	.xfilter('EMail,FirstName,LastName,FullName,Name') 
			// 	.sync()
			self.data = [
				{ "Key": "nostatus", "Name": _("No status")},
				{ "Key": "verified", "Name": _("Verified")},
				{ "Key": "unverified", "Name": _("Unverified")},
				{ "Key": "onverification", "Name": _("On verification")}
			];
			self.render();
		},
		render: function(){
			var self = this;
			//self.data = self.collection.feed();
			self.el.tmpl(self.template, self.data);
		}
	});
	return StatusesView;

});