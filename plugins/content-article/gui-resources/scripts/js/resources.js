define([
    'angular',
    'angular-resource'
],function(angular) {
    'use strict';

    var resources = angular.module('resources', ['ngResource']);

    resources.config(['$httpProvider', function($httpProvider) {
        // transforms related resources into ids
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
    }]);
 
    resources.factory('Article', ['$resource', function($resource) {
        return $resource('/resources/Article/:Id', {Id: '@Id'}, {
            update: {method: 'PUT'},
            save: {method: 'POST', params: {'X-Filter': 'Id'}}
        });
    }]);
});
