define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $window, desks, Desk, DeskService) {
        $scope.desks = desks;

        $scope.createDesk = function() {
            $scope.desk = {};
        };

        $scope.editDesk = function(desk) {
            $scope.orig = desk;
            angular.copy(desk, $scope.desk);
        };

        $scope.saveDesk = function() {
            if ('Id' in $scope.desk) {
                Desk.update($scope.desk, function() {
                    angular.extend($scope.orig, $scope.desk);
                });
            } else {
                Desk.save($scope.desk, function(desk) {
                    Desk.get({Id: desk.Id}, function(desk) {
                        $scope.desks.unshift(desk);
                    });
                });
            }
        };

        $scope.deleteDesk = function(desk, $index) {
            if ($window.confirm('Are you sure?')) {
                Desk.delete({Id: desk.Id}, function() {
                    $scope.desks.splice($index, 1);
                });
            }
        };

        $scope.addMembers = function(desk) {
            $scope.desk = desk;
            $scope.users = DeskService.getAvailableUsers(desk);
        };

        $scope.removeMember = function(desk, user) {
            DeskService.removeMember(desk, user);
            desk.members = DeskService.getMembers(desk);
        };
    };
});
