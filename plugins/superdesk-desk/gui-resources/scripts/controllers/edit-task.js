define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, Task, TaskStatusLoader) {
        $scope.statuses = TaskStatusLoader();

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
                        if (!$scope.parentTask) {
                            $scope.tasks.push(task);
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
