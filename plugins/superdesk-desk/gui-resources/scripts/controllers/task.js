define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, TaskService) {
        $q.when($scope.task).then(function(task) {
            TaskService.loadSubtasks(task).then(function(tasks) {
                $scope.task.subtasks = tasks;
            });
        });
    };
});
