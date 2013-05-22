define([
    'jquery',
    'backbone',
    'jquery/superdesk',
    config.guiJs('livedesk', 'action'),

    'jquery/tmpl',
    'tmpl!livedesk>error-notif'
], function($, Backbone, superdesk, BlogAction) {

    /**
     * Get blog href for given blog id
     *
     * @param {number} blogId
     * @return {string}
     */
    function getBlogHref(blogId) {
        return superdesk.apiUrl+'/resources/LiveDesk/Blog/' + blogId;
    }

    /**
     * Call blog action for given blog
     *
     * @param {string} actionId
     * @param {number} blogId
     * @return {function}
     */
    function callAction(actionId, blogId) {
        BlogAction.
            get(actionId).
            done(function(action) {
                var blogHref = getBlogHref(blogId);
                require([action.get('Script').href], function(app){ app(blogHref); });
            });
    }

    return Backbone.Router.extend({
        routes: {
            'live-blog/:id': 'liveBlogEdit',
            'live-blog/:id/config': 'liveBlogConfig',
            'live-blog/:id/collaborators': 'liveBlogCollaborators',
            'live-blog/:id/feeds': 'liveBlogFeeds',
            'live-blog-archive': 'liveBlogArchive'
        },

        liveBlogEdit: function(id) {
            var blogHref = getBlogHref(id);
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
            callAction('modules.livedesk.configure', id);
        },

        liveBlogCollaborators: function(id) {
            callAction('modules.livedesk.manage-collaborators', id);
        },

        liveBlogFeeds: function(id) {
            callAction('modules.livedesk.manage-feeds', id);
        },

        liveBlogArchive: function() {
            superdesk.showLoader();
            callAction('modules.livedesk.archive');
        }
    });
});
