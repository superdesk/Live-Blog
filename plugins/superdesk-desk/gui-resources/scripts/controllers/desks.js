define(['angular'],
function(angular) {
    return function($scope, $routeParams, desks, tasks, Task) {
        $scope.deskId = $routeParams.deskId;
        $scope.compact = false;
        $scope.list = false;
        $scope.desks = desks;
        $scope.tasks = tasks;

        $scope.boards = [
            {id: 'todo', key: 'to do', name: _('To Do') + ''},
            {id: 'inprogress', key: 'in progress', name: _('In Progress') + ''},
            {id: 'done', key: 'done', name: _('Done') + ''}
        ];

        $scope.addTask = function() {
            $scope.orig = {};
            $scope.task = {Status: 'to do', Desk: $scope.deskId};
        };

        $scope.editTask = function(task, index) {
            $scope.orig = task;
            $scope.task = {Title: task.Title, Status: task.Status.Key, Id: task.Id, DueDate: task.DueDate};
        };

        $scope.saveTask = function() {
            if ('Id' in $scope.task) {
                Task.update($scope.task, function(task) {
                    angular.extend($scope.orig, $scope.task);
                    $scope.orig.Status = {Key: $scope.task.Status};
                });
            } else {
                Task.save($scope.task, function(response) {
                    Task.get({Id: response.Id}, function(task) {
                        $scope.tasks.unshift(task);
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
