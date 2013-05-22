define(['angular'],
function(angular) {
    'use strict';

    return function($scope, Task, TaskStatusLoader) {
        $scope.statuses = TaskStatusLoader();
    };
});
