define(['angular'],
function(angular) {
    'use strict';

    return function($scope, DeskListLoader) {
        $scope.compact = false;
        $scope.list = false;

        DeskListLoader().then(function(desks) {
            $scope.desks = desks;
        });
    };
});
