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
    'desk/views/config',
    'superdesk/views/menu',
    'angular',
    'desk/controllers/config-desks',
    'tmpl!superdesk-desk>config-desks'
], function($, router, configView, menuView, angular, ConfigDesksController) {
    'use strict';

    return {
        init: function(submenu, menu, data) {
            menuView.addItem(data.feed());

            // define router when we have menu url
            router.route(data.get('NavBar'), 'config:desks', function() {
                var module = angular.module('desks.config', ['resources']);

                var template;
                $.tmpl('superdesk-desk>config-desks', {}, function(e, o) {
                    template = o;
                });

                module.config(['$routeProvider', function($routeProvider) {
                    $routeProvider.
                        when('/config/desks', {
                            controller: ConfigDesksController,
                            template: template,
                            resolve: {
                                desks: function(DeskListLoader) {
                                    return DeskListLoader();
                                }
                            }
                        });
                }]);

                module.config(['$interpolateProvider', function($interpolateProvider) {
                    $interpolateProvider.startSymbol('{{ ');
                    $interpolateProvider.endSymbol(' }}');
                }]);

                module.controller('DeskController', function($scope, DeskService) {
                    $scope.desk.members = DeskService.getMembers($scope.desk);
                    $scope.desk.cards = DeskService.getCards($scope.desk);
                });

                module.controller('AddMemberController', function($scope, DeskService) {
                    $scope.saveMembers = function(desk, users) {
                        angular.forEach(users, function(user) {
                            if (user.isSelected) {
                                DeskService.addMember(this, user);
                            }
                        }, desk);
                        desk.members = DeskService.getMembers(desk);
                    };
                });

                $('#area-main').attr('ng-view', '');
                angular.bootstrap('body', ['desks.config']);
            });
        }
    };
});
