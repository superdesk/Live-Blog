requirejs.config({
    paths: {
        'desks/views': config.gui('superdesk-desk/scripts/views')
    }
});

define([
    'jquery',
    'backbone',
    'desks/views/config'
], function($, Backbone, configView) {
    var Router = Backbone.Router.extend({
        routes: {
            'config/desks': 'config'
        },

        config: function() {
            configView.setElement($('#area-main'));
            configView.fetchCollection();
        }
    });

    new Router();
    Backbone.history.loadUrl();

    return {
        init: function(submenu, menu, data) {
            var list = $(submenu).empty(); // TODO create menu to controll top level menu
            $('<a href="#config/desks" />').text(data.get('Label')).appendTo(list).wrap('<li />');
        }
    }
});
