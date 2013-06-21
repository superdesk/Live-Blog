define([
    'jquery',
    'backbone',
    'router',
    'angular',
    config.guiJs('superdesk/article', 'controllers/article-list'),
    config.guiJs('superdesk/article', 'resources'),
    'tmpl!superdesk/article>list'
],
function($, backbone, router, angular, ArticleListController) {
    return function() {
        var module = angular.module('articles', ['resources']);

        module.config(['$interpolateProvider', function($interpolateProvider) {
            $interpolateProvider.startSymbol('{{ ');
            $interpolateProvider.endSymbol(' }}');
        }]);

        module.controller('ArticleListController', ArticleListController);

        $('#area-main').tmpl('superdesk/article>list');
        $('#area-main').attr('ng-controller', 'ArticleListController');
        angular.bootstrap(document, ['articles']);
    };
});
