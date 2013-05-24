define(['angular'],
function(angular) {
    'use strict';

    return function($scope, DeskListLoader) {
        $scope.desks = DeskListLoader();
    };
});
