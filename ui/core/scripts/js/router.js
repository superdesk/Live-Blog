define(['backbone'], function(Backbone) {
    var Router = {
        hasRoute: Backbone.history.start({root: config.lib_url + 'start.html'}),

        /**
         * Add route to global router and start
         */
        route: function(route, name, callback) {
            var router = new Backbone.Router();
            router.route(route, name, callback);
            this.start();
        },

        /**
         * Try to find a route matching current fragment
         * if non there was non before
         */
        start: function() {
            if (!this.hasRoute) {
                this.hasRoute = Backbone.history.loadUrl();
            }
        },

        /**
         * Reload route for current fragment
         */
        reload: function() {
            Backbone.history.loadUrl();
        }
    };

    return Router;
});
