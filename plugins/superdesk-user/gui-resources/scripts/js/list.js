define
([
    'jquery',
    'backbone',
    'router',
    'angular',
    config.guiJs('superdesk/user', 'controllers/user-list'),
    config.guiJs('superdesk/user', 'resources'),
    config.guiJs('superdesk/user', 'directives'),
    'tmpl!superdesk/user>list',
    'angular-bootstrap'
],

// TODO remove cleanup duplicate code

function($, backbone, router, angular, UserListController) {
    return function() {
        var module = angular.module('users', ['users.resources', 'users.directives', 'ui.bootstrap']);

        module.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);

        module.controller('UserListController', UserListController);

        $('#area-main').tmpl('superdesk/user>list');
        $('#area-main').attr('ng-controller', 'UserListController');
        angular.bootstrap(document, ['users']);
    };
});

