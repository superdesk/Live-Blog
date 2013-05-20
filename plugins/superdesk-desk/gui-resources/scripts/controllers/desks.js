define(['angular'],
function(angular) {
    return function($scope, desk, desks, tasks, Task) {
        $scope.compact = false;
        $scope.list = false;
        $scope.my = false;
        $scope.desk = desk;
        $scope.desks = desks;
        $scope.tasks = tasks;

        $scope.boards = [
            {id: 'todo', key: 'to do', name: _('To Do') + ''},
            {id: 'inprogress', key: 'in progress', name: _('In Progress') + ''},
            {id: 'done', key: 'done', name: _('Done') + ''}
        ];

        $scope.addTask = function() {
            $scope.orig = {};
            $scope.task = {Status: 'to do', Desk: desk.Id, User: null};
            $scope.users = desk.getUsers();
        };

        $scope.editTask = function(task, index) {
            $scope.orig = task;
            $scope.task = {
                Title: task.Title,
                Status: task.Status.Key,
                Id: task.Id,
                DueDate: task.DueDate,
                User: task.User,
                Description: task.Description
            };
            $scope.users = desk.getUsers();
        };

        $scope.setUser = function(user) {
            $scope.task.User = user;
        };

        $scope.getEditData = function() {
            var data = $scope.task;

            if (data.DueDate == $scope.orig.DueDate) {
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
                });
            } else {
                Task.save(data, function(response) {
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

        $scope.taskFilter = function(board) {
            return function(task) {
                if (board.key !== task.Status.Key) {
                    return false;
                }

                return !$scope.my || (task.User &&  task.User.Id == localStorage.getItem('superdesk.login.id'));
            };
        };

        $scope.hasTasks = function(board) {
            var filter = $scope.taskFilter(board);
            for (var i = 0; i < $scope.tasks.length; i++) {
                if (filter($scope.tasks[i])) {
                    return true;
                }
            }

            return false;
        };
    };
});
