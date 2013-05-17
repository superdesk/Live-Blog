define([
    'angular',
    'angular-resource'
],function(angular) {
    var resources = angular.module('resources', ['ngResource']);

    resources.factory('Desk', function($resource) {
        return $resource('/resources/Desk/Desk/:id', {id: '@Id'},
            {query: {method: 'GET', params: {'X-Filter': 'Id,Name,User'}, isArray: false}}
        );
    });

    resources.factory('TaskList', function($resource) {
        return $resource('/resources/Desk/Desk/:deskId/Task/?X-Filter=*');
    });

    resources.factory('Task', function($resource) {
        return $resource('/resources/Desk/Task/:Id', {Id: '@Id'},
            {update: {method: 'PUT'}, save: {method: 'POST', params: {'X-Filter': 'Id'}}}
        );
    });

    resources.factory('DeskLoader', ['Desk', '$q', function(Desk, $q) {
        return function() {
            var delay = $q.defer();
            Desk.query(function(response) {
                delay.resolve(response.DeskList);
            });
            return delay.promise;
        };
    }]);

    resources.factory('TaskLoader', ['TaskList', '$route', '$q', function(TaskList, $route, $q) {
        return function() {
            var delay = $q.defer();
            TaskList.get({deskId: $route.current.params.deskId}, function(response) {
                delay.resolve(response.TaskList);
            });
            return delay.promise;
        };
    }]);
});
