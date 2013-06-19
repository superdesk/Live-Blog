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
 
    resources.factory('Desk', ['$resource', '$q', function($resource, $q) {
        return $resource('/resources/Desk/Desk/:Id', {Id: '@Id'}, {
            query: {method: 'GET', params: {'X-Filter': '*,UserUnassigned'}, isArray: false},
            save: {method: 'POST', params: {'X-Filter': 'Id'}},
            update: {method: 'PUT'}
        });
    }]);

    resources.factory('Task', ['$resource', function($resource) {
        return $resource('/resources/Desk/Task/:Id', {Id: '@Id'},
            {update: {method: 'PUT'}, save: {method: 'POST', params: {'X-Filter': 'Id'}}}
        );
    }]);

    resources.factory('TaskComment', ['$resource', function($resource) {
        return $resource('/resources/Desk/TaskComment/:Id', {Id: '@Id'},
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

    resources.factory('File', function($resource) {
        return $resource('/resources/Archive/MetaData/:File', {File: '@Id'});
    });

    resources.service('TaskService', ['$resource', '$q', function($resource, $q) {
        var Task = $resource('/resources/Desk/Task/:taskId', {taskId: '@Id'}, {
            update: {method: 'PUT'}
        });

        var TaskFile = $resource('/resources/Desk/Task/:Task/MetaInfo', {}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': 'MetaData.*'}}
        });

        var TaskFileSaver = $resource('/resources/Desk/Task/:Task/MetaInfo/:File/File', {Task: '@Task', File: '@File'}, {
            save: {method: 'POST', params: {'X-Filter': '*'}}
        });

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

        this.saveTaskStatus = function(task) {
            Task.update({Id: task.Id, Status: task.Status.Key});
        };

        this.loadComments = function(task) {
            var comments = $resource('/resources/Desk/Task/:taskId/TaskComment', {taskId: task.Id}, {
                query: {method: 'GET', isArray: false, params: {'X-Filter': '*, User.*'}}
            });

            var delay = $q.defer();
            comments.query(function(response) {
                delay.resolve(response.TaskCommentList);
            });
        };

        this.getFiles = function(task) {
            var delay = $q.defer();
            TaskFile.query({Task: task.Id}, function(response) {
                var files = [];
                angular.forEach(response.MetaInfoList, function(metaInfo) {
                    files.push(metaInfo.MetaData);
                });

                delay.resolve(files);
            });

            return delay.promise;
        };

        this.addFile = function(task, file) {
            TaskFileSaver.save({Task: task.Id, File: file.Id});
        };

        this.removeFile = function(task, file) {
            TaskFileSaver.delete({Task: task.Id, File: file.Id});
        };

        var TaskLinkList = $resource('/resources/Desk/Task/:Task/TaskExternalLink', {}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}}
        });

        this.getLinks = function(task) {
            var delay = $q.defer();
            TaskLinkList.query({Task: task.Id}, function(response) {
                delay.resolve(response.TaskExternalLinkList);
            });

            return delay.promise;
        };

        var TaskLink = $resource('/resources/Desk/TaskExternalLink/:Id', {Id: '@Id'}, {
            save: {method: 'POST', params: {'X-Filter': 'Id'}},
            update: {method: 'PUT'}
        });

        this.saveLink = function(link) {
            if ('Id' in link) {
                TaskLink.update(link);
            } else {
                TaskLink.save(link);
            }
        };

        this.removeLink = function(link) {
            if ('Id' in link) {
                TaskLink.delete({Id: link.Id});
            }
        };
    }]);

    resources.service('DeskService', ['$resource', '$q', function($resource, $q) {
        var DeskMember = $resource('/resources/Desk/Desk/:deskId/User/:userId', {deskId: '@deskId', userId: '@userId'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*'}},
            save: {method: 'PUT'}
        });

        var DeskCard = $resource('/resources/Desk/Desk/:deskId/Card/:cardId', {deskId: '@deskId', cardId: '@Id'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*', 'asc': 'order'}},
            save: {method: 'POST', params: {'X-Filter': '*'}}
        });

        var Card = $resource('/resources/Desk/Card/:Id', {Id: '@Id'}, {
            save: {method: 'POST', params: {'X-Filter': '*'}}
        });

        var DeskTask = $resource('/resources/Desk/Desk/:deskId/Task', {deskId: '@deskId'}, {
            query: {method: 'GET', isArray: false, params: {'X-Filter': '*,User.*'}}
        });

        this.getMembers = function(desk) {
            var delay = $q.defer();

            $q.when(desk).then(function(desk) {
                DeskMember.query({deskId: desk.Id}, function(response) {
                    delay.resolve(response.UserList);
                });
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
            var users = $resource('/resources/Desk/Desk/:deskId/User/Unassigned', {deskId: '@deskId'}, {
                query: {method: 'GET', isArray: false, params: {'X-Filter': '*,MetaDataIcon'}}
            });

            var delay = $q.defer();
            users.query({deskId: desk.Id}, function(response) {
                delay.resolve(response.UserList);
            });

            return delay.promise;
        };

        this.getCards = function(desk) {
            var delay = $q.defer();

            $q.when(desk).then(function(desk) {
                DeskCard.query({deskId: desk.Id}, function(response) {
                    delay.resolve(response.CardList);
                });
            });

            return delay.promise;
        };

        this.saveCard = function(desk, card) {
            var delay = $q.defer();
            var data = angular.copy(card);
            data.Desk = desk.Id;
            Card.save(data, function(card) {
                delay.resolve(card);
            });
            return delay.promise;
        };

        this.deleteCard = function(card) {
            Card.delete({Id: card.Id});
        };

        this.getTasks = function(desk) {
            var delay = $q.defer();

            $q.when(desk).then(function(desk) {
                DeskTask.query({deskId: desk.Id}, function(response) {
                    delay.resolve(response.TaskList);
                });
            });

            return delay.promise;
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

        var CardPosition = $resource('/resources/Desk/Card/:card/Jump?jump=:jump', {card: '@Card', jump: '@jump'}, {
            update: {method: 'PUT'}
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

        this.moveCard = function(card, diff) {
            CardPosition.update({Card: card.Id, jump: diff});
        };
    }]);

    resources.service('UserService', ['$resource', '$q', function($resource, $q) {
        var UserImage = $resource('/resources/HR/Person/:userId/MetaData/Icon', {userId: '@userId'});

        this.getImage = function(user) {
            var delay = $q.defer();

            UserImage.get({userId: user.Id}, function(image) {
                delay.resolve(image);
            }, function() {
                delay.reject();
            });

            return delay.promise;
        };
    }]);

    var userId = localStorage['superdesk.login.id'];
    var authToken = localStorage['superdesk.login.session'];
    resources.value('uploadUrl', '/resources/my/HR/User/' + userId + '/MetaData/Upload?X-Filter=*&Authorization=' + authToken);
});
