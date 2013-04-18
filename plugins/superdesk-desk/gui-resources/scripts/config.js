requirejs.config({
    paths: {
        'superdesk/views': config.gui('superdesk/scripts/views'),
        'superdesk/models': config.gui('superdesk/scripts/models'),
        'desk/views': config.gui('superdesk-desk/scripts/views'),
        'desk/models': config.gui('superdesk-desk/scripts/models'),
        'desk/utils': config.gui('superdesk-desk/scripts/utils')
    }
});

define([
    'jquery',
    'backbone',
    'desk/views/config',
    'superdesk/views/menu'
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
    };
});
