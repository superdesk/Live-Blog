define(['angular'],
function(angular) {
    'use strict';

    return function($scope, DeskService) {
        $scope.desk.then(function(desk) {
            DeskService.getCards(desk).then(function(cards) {
                $scope.cards = cards;
            });
        });
    };
});
