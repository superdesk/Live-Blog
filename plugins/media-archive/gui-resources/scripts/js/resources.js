define(['angular', 'angular-resource'], function(angular) {
    'use strict';

    var module = angular.module('superdesk.media-archive.resources', ['ngResource']);

    module.factory('MetaDataQuery', function($resource) {
        return $resource('/resources/Archive/MetaDataInfo/Query', {}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}}
        });
    });

    module.service('MediaSearchService', function($q, MetaDataQuery) {
        this.find = function() {
            var delay = $q.defer();
            MetaDataQuery.query({}, function(response) {
                delay.resolve(response.MetaDataInfoList);
            });

            return delay.promise;
        };
    });
});
