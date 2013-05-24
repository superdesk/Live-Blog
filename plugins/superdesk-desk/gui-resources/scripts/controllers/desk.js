define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, DeskService) {
        $q.when($scope.desk).then(function(desk) {
            DeskService.getCards(desk).then(function(cards) {
                $scope.cards = cards;
            });

            DeskService.getTasks(desk).then(function(tasks) {
                $scope.$parent.tasks = tasks;
            });

            DeskService.getMembers(desk).then(function(users) {
                $scope.$parent.users = users;
            });
        });
    };
});
