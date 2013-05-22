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

    resources.factory('Task', ['$resource', function($resource) {
        return $resource('/resources/Desk/Task/:Id', {Id: '@Id'},
            {update: {method: 'PUT'}, save: {method: 'POST', params: {'X-Filter': 'Id'}}}
        );
    }]);

    resources.factory('TaskStatus', ['$resource', function($resource) {
        return $resource('/resources/Desk/TaskStatus/:Id', {Id: '@Id'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}},
            save: {method: 'POST', params: {'X-Filter': '*'}}

        });
    }]);

    resources.factory('TaskStatusLoader', ['TaskStatus', '$q', function(TaskStatus, $q) {
        return function() {
            var delay = $q.defer();
            TaskStatus.query({}, function(response) {
                delay.resolve(response.TaskStatusList);
            });

            return delay.promise;
        };
    }]);

    resources.factory('DeskLoader', ['Desk', 'deskId', '$q', function(Desk, deskId, $q) {
        return function() {
            var delay = $q.defer();
            Desk.get({Id: deskId}, function(desk) {
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

    resources.factory('DeskTaskLoader', ['TaskList', 'deskId', '$q', function(TaskList, deskId, $q) {
        return function() {
            var delay = $q.defer();

            TaskList.get({deskId: deskId}, function(response) {
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

    resources.service('DeskService', ['$resource', '$q', function($resource, $q) {
        var DeskMember = $resource('/resources/Desk/Desk/:deskId/User/:userId', {deskId: '@deskId', userId: '@userId'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}},
            save: {method: 'PUT'}
        });

        var DeskCard = $resource('/resources/Desk/Desk/:deskId/Card/:cardId', {deskId: '@deskId', cardId: '@Id'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}},
            save: {method: 'POST', params: {'X-Filter': '*'}}
        });

        var Card = $resource('/resources/Desk/Card/:Id', {Id: '@Id'}, {
            save: {method: 'POST', params: {'X-Filter': '*'}}
        });

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
            var delay = $q.defer();
            DeskCard.query({deskId: desk.Id}, function(response) {
                delay.resolve(response.CardList);
            });

            return delay.promise;
        };

        this.saveCard = function(desk, card) {
            var delay = $q.defer();
            var data = angular.copy(card);
            data['Desk'] = desk.Id;
            Card.save(data, function(card) {
                delay.resolve(card);
            });
            return delay.promise;
        };

        this.deleteCard = function(card) {
            Card.delete({Id: card.Id});
        };
    }]);

    resources.service('CardService', ['$resource', '$q', function($resource, $q) {
        var CardStatus = $resource('/resources/Desk/Card/:cardId/TaskStatus/:statusKey', {cardId: '@Card', statusKey: '@TaskStatus'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': 'Key'}},
            save: {method: 'PUT'}
        });

        var AvailableStatus = $resource('/resources/Desk/Card/:cardId/TaskStatus/Unassigned', {cardId: '@cardId'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': 'Key'}}
        });

        this.getStatuses = function(card) {
            var delay = $q.defer();
            CardStatus.query({cardId: card.Id}, function(response) {
                delay.resolve(response.TaskStatusList);
            });
            return delay.promise;
        };

        this.getAvailableStatuses = function(card) {
            var delay = $q.defer();
            AvailableStatus.query({cardId: card.Id}, function(response) {
                delay.resolve(response.TaskStatusList);
            });

            return delay.promise;
        };

        this.addStatus = function(card, stat) {
            CardStatus.save({Card: card.Id, TaskStatus: stat.Key});
        };

        this.removeStatus = function(card, stat) {
            var res = new CardStatus({Card: card.Id, TaskStatus: stat.Key});
            res.$delete();
        };
    }]);
});
