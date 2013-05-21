define([
    'angular',
    'angular-resource'
],function(angular) {

    function parseUrl(url) {
        return url.replace('http://localhost:8080', '');
    }

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

    resources.factory('Desk', ['$resource', '$q', function($resource, $q) {
        var Desk = $resource('/resources/Desk/Desk/:Id', {Id: '@Id'}, {
            query: {method: 'GET', params: {'X-Filter': '*,UserUnassigned'}, isArray: false},
            save: {method: 'POST', params: {'X-Filter': 'Id'}},
            update: {method: 'PUT'}
        });

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

    resources.factory('Task', ['$resource', function($resource, $q) {
        return $resource('/resources/Desk/Task/:Id', {Id: '@Id'},
            {update: {method: 'PUT'}, save: {method: 'POST', params: {'X-Filter': 'Id'}}}
        );
    }]);

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

    resources.service('TaskService', ['$resource', '$q', function($resource, $q) {
        this.loadSubtasks = function(task) {
            var tasks = $resource('/resources/Desk/Task/:taskId/Task', {taskId: task.Id}, {
                query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}}
            });

            var delay = $q.defer();
            tasks.query(function(response) {
                delay.resolve(response.TaskList);
            });

            return delay.promise;
        };
    }]);

    resources.factory('DeskMember', ['$resource', function($resource) {
        return $resource('/resources/Desk/Desk/:deskId/User/:userId', {deskId: '@deskId', userId: '@userId'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}},
            save: {method: 'PUT'}
        });
    }]);

    resources.service('DeskService', ['$resource', '$q', 'DeskMember', function($resource, $q, DeskMember) {
        this.getMembers = function(desk) {
            var delay = $q.defer();
            DeskMember.query({deskId: desk.Id}, function(response) {
                delay.resolve(response.UserList);
            });

            return delay.promise;
        };

        this.addMember = function(desk, user) {
            DeskMember.save({deskId: desk.Id, userId: user.Id});
        };

        this.removeMember = function(desk, user) {
            DeskMember.delete({deskId: desk.Id, userId: user.Id});
        };

        this.getAvailableUsers = function(desk) {
            var users = $resource(parseUrl(desk.UserUnassigned.href), {}, {
                query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}}
            });

            var delay = $q.defer();
            users.query(function(response) {
                delay.resolve(response.UserList);
            });

            return delay.promise;
        };

        this.getCards = function(desk) {
            return [
                {Id: 'todo', Key: 'to do', Name: _('To Do')},
                {Id: 'inprogress', Key: 'in progress', Name: _('In Progress')},
                {Id: 'done', Key: 'done', Name: _('Done')}
            ];
        };
    }]);
});
