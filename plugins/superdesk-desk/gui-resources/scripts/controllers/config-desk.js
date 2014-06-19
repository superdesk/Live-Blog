define(['angular'],
function(angular) {
    'use strict';

    return function($scope, DeskService, CardService) {
        $scope.desk.members = DeskService.getMembers($scope.desk);

        DeskService.getCards($scope.desk).then(function(cards) {
            $scope.desk.cards = cards;
            $scope.removeFromAllCards = function(stat) {
                angular.forEach($scope.desk.cards, function(card) {
                    for (var i in card.statuses) {
                        if (card.statuses[i].Key === stat.Key) {
                            CardService.removeStatus(card, stat);
                            card.statuses.splice(i, 1);
                            break;
                        }
                    }
                });
            };
        });
    };
});
