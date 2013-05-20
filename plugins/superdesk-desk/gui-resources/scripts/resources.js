define([
    'angular',
    'angular-resource'
],function(angular) {

    function parseUrl(url) {
        return url.replace('http://localhost:8080', '');
    }

    var resources = angular.module('resources', ['ngResource']);

    resources.config(['$httpProvider', function($httpProvider) {
        // transforms related objects to id
        $httpProvider.defaults.transformRequest = function(data) {
            for (var key in data) {
                if (typeof data[key] === 'object' && 'Id' in data[key]) {
                    data[key] = data[key].Id;
                }
            }
            return angular.toJson(data);
        };
    }]);

    resources.factory('Desk', ['$resource', '$q', function($resource, $q) {
        var Desk = $resource('/resources/Desk/Desk/:id', {id: '@Id'},
            {query: {method: 'GET', params: {'X-Filter': 'Id,Name,User'}, isArray: false}}
        );

        Desk.prototype = {
            getUsers: function() {
                var Users = $resource(parseUrl(this.User.href), {}, {query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}}});
                var delay = $q.defer();
                Users.query(function(response) {
                    delay.resolve(response.UserList);
                });
                return delay.promise;
            }
        };

        return Desk;
    }]);

    resources.factory('TaskList', function($resource) {
        return $resource('/resources/Desk/Desk/:deskId/Task/?X-Filter=*,User.*');
    });

    resources.factory('Task', function($resource) {
        return $resource('/resources/Desk/Task/:Id', {Id: '@Id'},
            {update: {method: 'PUT'}, save: {method: 'POST', params: {'X-Filter': 'Id'}}}
        );
    });

    resources.factory('DeskLoader', ['Desk', '$route', '$q', function(Desk, $route, $q) {
        return function() {
            var delay = $q.defer();
            Desk.get({id: $route.current.params.deskId}, function(desk) {
                delay.resolve(desk);
            });
            return delay.promise;
        };
    }]);

    resources.factory('DeskListLoader', ['Desk', '$q', function(Desk, $q) {
        return function() {
            var delay = $q.defer();
            Desk.query(function(response) {
                delay.resolve(response.DeskList);
            });
            return delay.promise;
        };
    }]);

    resources.factory('TaskListLoader', ['TaskList', '$route', '$q', function(TaskList, $route, $q) {
        return function() {
            var delay = $q.defer();
            TaskList.get({deskId: $route.current.params.deskId}, function(response) {
                delay.resolve(response.TaskList);
            });
            return delay.promise;
        };
    }]);

    resources.factory('DeskUserLoader', ['$resource', '$q',  function($resource, $q) {
        return function(desk) {
            console.log(desk.User);
        };
    }]);
});
