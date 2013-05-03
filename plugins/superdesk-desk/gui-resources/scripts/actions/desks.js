requirejs.config({
    paths: {
        'angular': 'https://ajax.googleapis.com/ajax/libs/angularjs/1.0.6/angular',
        'angular-resource': 'http://code.angularjs.org/1.0.6/angular-resource'
    },
    shim: {
        'angular': {exports: 'angular'},
        'angular-resource': {deps: ['angular']}
    }
});

define([
    'jquery',
    'backbone',
    'router',
    'desk/models/desk-collection',
    'desk/views/single-desk',
    'angular',
    'angular-resource'
],function($, Backbone, router, DeskCollection, DeskBoardsView, angular) {
    var DeskMenuView = Backbone.View.extend({
        tagName: 'li',
        render: function() {
            var link = $('<a />').text(this.model.get('Name')).attr('href', '#desks/' + this.model.id);
            $(this.el).html(link);
            return this;
        }
    });

    var MenuView = Backbone.View.extend({
        initialize: function() {
            this.collection.on('reset', this.render, this);
        },

        render: function() {
            var list = $(this.el).empty();
            this.collection.each(function(desk) {
                var view = new DeskMenuView({model: desk});
                list.append(view.render().el);
            });
        }
    });

    router.route('desks/:id', 'desk', function singleDesk(deskId) {
        $('#area-main').tmpl('superdesk-desk>desk/single').attr('ng-controller', 'TasksController');

        var app = angular.module('deskMod', ['ngResource']);
        app.controller('TasksController', ['$scope', '$resource', function($scope, $resource) {
            var Desk = $resource('/resources/Desk/Desk/:id');
            var Task = $resource('/resources/Desk/Desk/:deskId/Task/:taskId?X-Filter=*', {'taskId': '@Id'});

            $scope.compact = false;
            $scope.list = false;
            $scope.task = {};
            $scope.orig = null;

            $scope.boards = [
                {id: 'todo', key: 'to do', name: _('To Do') + ''},
                {id: 'inprogress', key: 'in progress', name: _('In Progress') + ''},
                {id: 'done', key: 'done', name: _('Done') + ''}
            ];

            $scope.desk = Desk.get({id: deskId});
            Task.get({deskId: deskId}, function(tasks) {
                $scope.tasks = tasks.TaskList;
            });

            $scope.editTask = function(task, index) {
                $scope.orig = task;
                $scope.index = index;
                if (task) {
                    $scope.task = {
                        Title: task.Title,
                        Status: task.Status.Key,
                        Id: task.Id
                    };
                } else {
                    $scope.task = {Status: 'to do', Desk: deskId};
                }
            };

            $scope.saveTask = function() {
                if ('Id' in $scope.task) {
                    var res = $resource('/resources/Desk/Task/:id', {id: '@Id'}, {update: {method: 'PUT'}});
                    res.update($scope.task, function(task) {
                        angular.extend($scope.orig, $scope.task);
                        $scope.orig.Status = {Key: $scope.task.Status};
                    });
                } else {
                    var res = $resource('/resources/Desk/Task/:Id?X-Filter=Id', {Id: '@Id'});
                    res.save($scope.task, function(response) {
                        res.get({Id: response.Id}, function(task) {
                            $scope.tasks.unshift(task);
                        });
                    });
                }
            };

            $scope.deleteTask = function() {
                if ($scope.index !== undefined) {
                    var res = $resource('/resources/Desk/Task/:Id', {Id: '@Id'});
                    res.remove({Id: $scope.task.Id});
                    $scope.tasks.splice($scope.index, 1);
                }
            };
        }]);

        angular.bootstrap('#area-main', ['deskMod']);
        return;

        var view = new DeskBoardsView({model: desk, el: '#area-main'});
    });

    router.route('desks', 'desks', function allDesks() {
        // noop
    });

    return {
        init: function(submenu, menu, data) {
            var desks = new DeskCollection();
            var menu = new MenuView({el: submenu, collection: desks});
            var timeout = 5000;

            function fetchDesks() {
                desks.fetch({reset: true, headers: desks.xfilter});
                setTimeout(fetchDesks, timeout);
            };

            desks.xfilter = {'X-Filter': 'Id, Name'};
            fetchDesks();
        }
    };
});
