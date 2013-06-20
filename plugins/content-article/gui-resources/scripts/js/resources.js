define([
    'angular',
    'angular-resource'
],function(angular) {
    'use strict';

    var resources = angular.module('articles.resources', ['ngResource']);

    resources.factory('Article', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/Content/Article/:Id/:Action', {Id: '@Id', Action: '@Action'}, {
            query: {method: 'GET', params: {'X-Filter': '*,Author.*'}},
            update: {method: 'PUT'},
            save: {method: 'POST', params: {'X-Filter': 'Id'}}
        });
    }]);

    resources.factory('ArticleListLoader', ['Article', '$q', function(Article, $q) {
        return function(offset, limit, searchTerm) {
            var delay = $q.defer();
            var parameters = {offset: offset, limit: limit};
            if (searchTerm !== undefined && searchTerm !== '') {
                parameters.search = searchTerm;
            }
            Article.query(parameters, function(response) {
                for (var i = 0; i < response.ArticleList.length; i = i + 1) {
                    response.ArticleList[i].checked = false;
                    response.ArticleList[i].Content = angular.fromJson(response.ArticleList[i].Content);
                    if (response.ArticleList[i].IsPublished === 'True') {
                        response.ArticleList[i].IsPublished = true;
                    } else {
                        response.ArticleList[i].IsPublished = false;
                    }
                }
                response.ArticleList.count = response.total;
                delay.resolve(response.ArticleList);
            });
            return delay.promise;
        };
    }]);
});
