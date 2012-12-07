define([
	'jquery',
	'gizmo/superdesk',
	'jquery/rest',
	'jquery/avatar',
	config.guiJs('livedesk', 'models/collaborators'),
	config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/collaborator'),
	'tmpl!livedesk>layouts/livedesk',
	'tmpl!livedesk>layouts/blog',
	'tmpl!livedesk>manage-collaborators',
	'tmpl!livedesk>manage-collaborators/internal-colabs'
	], function ($, Gizmo, Collaborators) {

	var CollaboratorView = Gizmo.View.extend({
		
	}),
	ManageInternalCollaboratorsView = Gizmo.View.extend({
		init: function(){

		}
	}),
	MainManageCollaboratorsView = Gizmo.View.extend({
		refresh: function () {
			var self = this;
			self.model = Gizmo.Auth(new Gizmo.Register.Blog(self.theBlog));
			self.model
				.on('read', self.render, self)
				.sync();
		},
		render: function(evt, data) {

		}
	});
	var mainManageCollaboratosView = new MainManageCollaboratorsView({
		el: '#area-main'
	});
	return app = function (theBlog) {
		mainManageCollaboratosView.theBlog = theBlog;
		mainManageCollaboratosView.refresh();
	}
});