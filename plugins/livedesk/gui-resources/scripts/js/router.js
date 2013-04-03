define
([
  'jquery', 'jquery/superdesk',
  config.guiJs('livedesk', 'action'),
  'gizmo/superdesk/action'
], function($, superdesk, BlogAction, Action)
{
    return Backbone.Router.extend({
        routes: {
            'live-blog/:id': 'liveBlogEdit',
            'live-blog/:id/config': 'liveBlogConfig',
            'live-blog/:id/collaborators': 'liveBlogCollaborators',
            'live-blog/:id/feeds': 'liveBlogFeeds',
            'live-blog-archive': 'liveBlogArchive'
        },

        getBlogHref: function(id) {
            return '/resources/LiveDesk/Blog/' + id;
        },

        liveBlogEdit: function(id) {
            var blogHref = this.getBlogHref(id);
            BlogAction.setBlogUrl(blogHref);
            BlogAction.
                get('modules.livedesk.edit').
                done(function(action) {
                    superdesk.showLoader();
                    if (!action) {
                        return;
                    }

                    require([action.get('Script').href], function(EditApp){ EditApp(blogHref); });
                }).
                fail(function() {
                    $.tmpl('livedesk>error-notif', {Error: _('You cannot perform this action')}, function(e, o) {
                        $('#area-main').append($(o));
                        $('.close', $(o)).on('click', function(){ $(o).remove(); });
                        setTimeout(function(){ $(o).remove(); }, 3000);
                    });
                });
        },

        liveBlogConfig: function(id) {
            var blogHref = this.getBlogHref(id);
            BlogAction.
                get('modules.livedesk.configure').
                done(function(action) {
                    require([action.get('Script').href], function(app){ new app(blogHref); });
                });
        },

        liveBlogCollaborators: function(id) {
            var blogHref = this.getBlogHref(id);
            BlogAction.
                get('modules.livedesk.manage-collaborators').
                done(function(action) {
                    require([action.get('Script').href], function(app){ new app(blogHref); });
                });
        },

        liveBlogFeeds: function(id) {
            var blogHref = this.getBlogHref(id);
            BlogAction.
                get('modules.livedesk.manage-feeds').
                done(function(action) {
                    require([action.get('Script').href], function(app) {
                        app(blogHref);
                    });
                });
        },

        liveBlogArchive: function() {
            superdesk.showLoader();
            Action.
                get('modules.livedesk.archive').
                done(function(action) {
                    require([action.get('Script').href], function(app){ new app(); });
                });
        }
    });
});
