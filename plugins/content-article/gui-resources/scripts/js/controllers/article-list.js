define(['angular'],
function(angular) {
    'use strict';

    return function($scope, $q, Article) {
        $scope.getList = function() {
            console.log(123);
        };

        $scope.getList();
    };
});
