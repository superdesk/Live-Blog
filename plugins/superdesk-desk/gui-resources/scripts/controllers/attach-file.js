define(['angular'], function(angular) {
    'use strict';

    return function($scope, $q, TaskService, MediaSearchService) {
        $scope.files = [];

        $scope.reset = function() {
            $scope.files = [];
            $scope.items = [];
            $scope.$emit('files:reset');
        };

        $scope.save = function(task) {
            angular.forEach($scope.files, function(file) {
                TaskService.addFile(task, file);
                $q.when(task.files, function(files) {
                    files.push(file);
                });
            });

            angular.forEach($scope.items, function(item) {
                if (item.selected) {
                    TaskService.addFile(task, item);
                    $q.when(task.files, function(files) {
                        files.push(item);
                    });
                }
            });
        };

        $scope.searchMedia = function(task) {
            MediaSearchService.find().then(function(items) {
                $scope.items = items;
            });
        };
    };
});
