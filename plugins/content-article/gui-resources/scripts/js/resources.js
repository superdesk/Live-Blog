define([
    'angular',
    'angular-resource'
],function(angular) {
    'use strict';

    var resources = angular.module('resources', ['ngResource']);

    resources.config(['$httpProvider', function($httpProvider) {
        // transforms related resources into ids
        /*
        $httpProvider.defaults.transformRequest = function(data) {
            var update = {};
            angular.forEach(data, function(value, key) {
                if (value && typeof value === 'object') {
                    this[key] = 'Key' in value ? value.Key : value.Id;
                } else if (key !== 'href') {
                    this[key] = value;
                }
            }, update);
            return angular.toJson(update);
        };
        */
    }]);
 
    resources.factory('Article', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/Content/Article/:Id', {Id: '@Id'}, {
            query: {method: 'GET', params: {'X-Filter': '*'}},
            update: {method: 'PUT'},
            save: {method: 'POST', params: {'X-Filter': 'Id'}}
        });
    }]);

    resources.factory('ArticleListLoader', ['Article', '$q', function(Article, $q) {
        return function() {
            var delay = $q.defer();
            Article.query(function(response) {
                delay.resolve(response.ArticleList);
            });
            return delay.promise;
        };
    }]);
});
