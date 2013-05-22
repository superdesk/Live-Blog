define(['angular'],
function(angular) {
    'use strict';

    return function($scope, CardService) {
        $scope.card.statuses = [];

        CardService.getStatuses($scope.card).then(function(statuses) {
            $scope.card.statuses = statuses;

            $scope.findStatus = function(stat) {
                var stats = $scope.card.statuses;
                for (var i in stats) {
                    if (stats[i].Key === stat.Key) {
                        return i;
                    }
                }

                return false;
            };

            $scope.hasStatus = function(stat) {
                return $scope.findStatus(stat) !== false;
            };

            $scope.toggleStatus = function(card, stat) {
                var index = $scope.findStatus(stat);
                if (index !== false) {
                    CardService.removeStatus(card, stat);
                    $scope.card.statuses.splice(index, 1);
                } else {
                    $scope.removeFromAllCards(stat);
                    CardService.addStatus(card, stat);
                    $scope.card.statuses.push(stat);
                }
            };
        });
    };
});
