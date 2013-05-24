define(['angular'],
function(angular) {
    'use strict';

    return function($scope, CardService) {
        CardService.getStatuses($scope.card).then(function(statuses) {
            $scope.card.statuses = statuses;

            $scope.isCardTask = function(task) {
                for (var i in statuses) {
                    if (statuses[i].Key === task.Status.Key) {
                        return true;
                    }
                }
            };

            $scope.isUserTask = function(task) {
                return task.User && task.User.Id == localStorage.getItem('superdesk.login.id'); // TODO create user service
            };

            $scope.isMyTask = function(task) {
                return !$scope.my || $scope.isUserTask(task);
            };

            $scope.isEmpty = function(tasks) {
                for (var i in tasks) {
                    if ($scope.isCardTask(tasks[i]) && $scope.isMyTask(tasks[i])) {
                        return false;
                    }
                }

                return true;
            }
        });
    };
});
