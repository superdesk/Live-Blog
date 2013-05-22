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
        });
    };

});
