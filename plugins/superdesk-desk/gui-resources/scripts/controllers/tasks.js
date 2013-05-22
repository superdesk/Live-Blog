define(['angular'],
function(angular) {
    'use strict';

    return function($scope, desk, desks, tasks, Task, TaskService) {
        $scope.compact = false;
        $scope.list = false;
        $scope.my = false;
        $scope.desk = desk;
        $scope.desks = desks;
        $scope.tasks = tasks;
        $scope.users = desk.getUsers();

        $scope.boards = [
            {id: 'todo', key: 'to do', name: _('To Do') + ''},
            {id: 'inprogress', key: 'in progress', name: _('In Progress') + ''},
            {id: 'done', key: 'done', name: _('Done') + ''}
        ];

        $scope.addTask = function(parentTask) {
            $scope.orig = {};
            $scope.task = {Status: 'to do', Desk: desk.Id, User: null, Parent: parentTask};
            $scope.parentTask = parentTask;
        };

        $scope.editTask = function(task, parentTask) {
            $scope.orig = task;
            $scope.task = {
                Id: task.Id,
                Title: task.Title,
                Status: task.Status.Key,
                DueDate: task.DueDate,
                User: task.User,
                Description: task.Description
            };
            $scope.subtasks = TaskService.loadSubtasks($scope.orig);
            $scope.parentTask = parentTask;
        };

        $scope.deleteTask = function() {
            if ('Id' in $scope.task) {
                Task.remove({Id: $scope.task.Id});
                var index = $scope.tasks.indexOf($scope.orig);
                $scope.tasks.splice(index, 1);
            }
        };

        $scope.isBoardTask = function(task, board) {
            return board.key === task.Status.Key;
        };

        $scope.isUserTask = function(task, user) {
            return task.User && task.User.Id == localStorage.getItem('superdesk.login.id'); // TODO create user service
        };

        $scope.isMyTask = function(task) {
            return !$scope.my || $scope.isUserTask(task);
        };

        $scope.isUserBoardTask = function(board) {
            return function(task) {
                return $scope.isBoardTask(task, board) && (!$scope.my || $scope.isUserTask(task));
            };
        };

        $scope.hasTasks = function(board) {
            var filter = $scope.isUserBoardTask(board);
            for (var i = 0; i < $scope.tasks.length; i++) {
                if (filter($scope.tasks[i])) {
                    return true;
                }
            }

            return false;
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
                    $scope.orig.Status = {Key: $scope.task.Status};
                    $scope.orig.User = $scope.task.User;
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
