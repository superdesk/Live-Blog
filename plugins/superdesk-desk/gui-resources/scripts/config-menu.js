requirejs.config({
    paths: {
        'config/views': config.gui('superdesk/scripts/views'),
        'desks/views': config.gui('superdesk-desk/scripts/views')
    }
});

define([
    'jquery',
    'backbone',
    'desks/views/config',
    'config/views/menu'
], function($, Backbone, configView, menuView) {
    return {
        init: function(submenu, menu, data) {
            menuView.addItem(data.feed());

            // define router when we have menu url
            var router = new Backbone.Router();
            router.route(data.get('NavBar'), 'config:desks', function() {
                configView.setElement($('#area-main'));
                configView.fetchCollection();
            });

            Backbone.history.loadUrl();
        }
    }
});
