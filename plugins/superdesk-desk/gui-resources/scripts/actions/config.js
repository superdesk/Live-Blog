requirejs.config({
    paths: {
        'superdesk/views': config.gui('superdesk/scripts/views'),
        'superdesk/models': config.gui('superdesk/scripts/models'),
        'desk': config.gui('superdesk-desk/scripts')
    }
});

define([
    'jquery',
    'router',
    'superdesk/views/menu',
    'angular',
    'desk/controllers/config-desks',
    'desk/controllers/config-desk',
    'desk/controllers/config-card',
    'desk/controllers/config-add-member',
    'desk/resources',
    'desk/directives',
    'tmpl!superdesk-desk>config-desks'
], function($, router, menuView, angular, ConfigDesksController, ConfigDeskController, ConfigCardController, ConfigAddMemberController) {
    'use strict';

    return {
        init: function(submenu, menu, data) {
            menuView.addItem(data.feed());

            // define router when we have menu url
            router.route(data.get('NavBar'), 'config:desks', function() {
                var module = angular.module('desks.config', ['desks.resources', 'desks.directives']);

                module.config(['$interpolateProvider', function($interpolateProvider) {
                    $interpolateProvider.startSymbol('{{ ');
                    $interpolateProvider.endSymbol(' }}');
                }]);

                module.controller('ConfigDesksController', ConfigDesksController);
                module.controller('DeskController', ConfigDeskController);
                module.controller('CardController', ConfigCardController);
                module.controller('AddMemberController', ConfigAddMemberController);

                $('#area-main').tmpl('superdesk-desk>config-desks');
                $('#area-main').attr('ng-controller', 'ConfigDesksController');
                angular.bootstrap(document, ['desks.config']);
            });
        }
    };
});
