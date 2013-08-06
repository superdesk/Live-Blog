define
([
    'jquery',
    'backbone',
    'router',
    'angular',
    config.guiJs('superdesk/user', 'controllers/user-list'),
    config.guiJs('superdesk/article', 'resources'),
    config.guiJs('superdesk/article', 'directives/checkbox'),
    'tmpl!superdesk/user>list',
    'angular-bootstrap'
],

// TODO remove cleanup duplicate code

function($, backbone, router, angular, UserListController) {
    return function() {
        var module = angular.module('users', ['users.resources', 'ui.bootstrap']);

        module.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);

        module.controller('UserListController', UserListController);

        $('#area-main').tmpl('superdesk/article>list');
        $('#area-main').attr('ng-controller', 'UserListController');
        angular.bootstrap(document, ['users']);
    };
});

