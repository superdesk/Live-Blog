define(['angular'],
function(angular) {
    'use strict';

    return function($scope, DeskLoader, DeskListLoader, DeskTaskLoader, Task, TaskService) {
        $scope.compact = false;
        $scope.list = false;
        $scope.my = false;

        DeskListLoader().then(function(desks) {
            $scope.desks = desks;
        });

        DeskTaskLoader().then(function(tasks) {
            $scope.tasks = tasks;
        });

        $scope.desk = DeskLoader();
        $scope.desk.then(function(desk) {
            $scope.users = desk.getUsers();
            $scope.deskId = desk.Id;
        });

        $scope.addTask = function(parentTask) {
            $scope.orig = {};
            $scope.task = {Status: 'to do', Desk: $scope.deskId, User: null, Parent: parentTask};
            $scope.parentTask = parentTask;
        };

        $scope.editTask = function(task, parentTask) {
            $scope.orig = task;
            $scope.task = {
                Id: task.Id,
                Title: task.Title,
                Status: task.Status,
                DueDate: task.DueDate,
                User: task.User,
                Description: task.Description
            };
            $scope.subtasks = TaskService.loadSubtasks($scope.orig);
            $scope.parentTask = parentTask;
        };

        $scope.getEditData = function() {
            var data = $scope.task;

            if (data.DueDate === $scope.orig.DueDate) {
                delete data.DueDate; // TODO api does not accepts data in same format it sends them..
            }

            return data;
        };

        $scope.saveTask = function() {
            var data = $scope.getEditData();
            if ('Id' in $scope.task) {
                Task.update(data, function(task) {
                    angular.extend($scope.orig, $scope.task);
                    $scope.orig.User = $scope.task.User;
                    $scope.orig.Status = {Key: $scope.task.Status.Key};
                });
            } else {
                Task.save(data, function(response) {
                    Task.get({Id: response.Id}, function(task) {
                        if (!task.Parent) {
                            $scope.tasks.unshift(task);
                        }
                    });
                });
            }
        };

        $scope.deleteTask = function() {
            if ('Id' in $scope.task) {
                Task.remove({Id: $scope.task.Id});
                var index = $scope.tasks.indexOf($scope.orig);
                $scope.tasks.splice(index, 1);
            }
        };
    };
});
