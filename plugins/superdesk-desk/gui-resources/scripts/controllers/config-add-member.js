define(['angular'],
function(angular) {
    'use strict';

    return function($scope, DeskService) {
        $scope.saveMembers = function(desk, users) {
            angular.forEach(users, function(user) {
                if (user.isSelected) {
                    DeskService.addMember(this, user);
                }
            }, desk);
            desk.members = DeskService.getMembers(desk);
        };
    };
});
